---
title: Evaluation — Evaluation Methods
doc_source:
  - https://langfuse.com/docs/evaluation/evaluation-methods/llm-as-a-judge
  - https://langfuse.com/docs/evaluation/evaluation-methods/code-evaluators
  - https://langfuse.com/docs/evaluation/evaluation-methods/annotation-queues
  - https://langfuse.com/docs/evaluation/evaluation-methods/scores-via-ui
  - https://langfuse.com/docs/evaluation/evaluation-methods/scores-via-sdk
accessed: 2026-07-31
version: v4
status: draft
---

# Evaluation Methods

Năm cách sinh `score` gắn lên trace, observation, session hoặc dataset run trong Langfuse; khác nhau ở chỗ **ai chấm** và **bằng cơ chế nào**.

## Tổng quan

Điểm chung gom năm phương pháp này: mọi phương pháp đều kết thúc bằng một `score` gắn vào dữ liệu đã trace, dùng chung bốn kiểu dữ liệu (Numeric, Categorical, Boolean, Text) và cùng khái niệm target *Observations* (dữ liệu production) so với *Experiments* (dataset thử nghiệm có kiểm soát). Cái khác nằm ở nguồn sinh score.

**LLM-as-a-Judge** để một model chấm chất lượng output theo rubric; **Code evaluators** chạy logic Python/TS xác định do Langfuse thực thi; **Scores via API/SDK** nhận score do app/pipeline bên ngoài tự tính rồi đẩy vào; **Scores via UI** cho người chấm tay trực tiếp trên một item; **Annotation Queues** tổ chức việc chấm tay đó thành luồng phân công cho nhiều người trên batch lớn.

## 1. LLM-as-a-Judge

**Khái niệm.** Phương pháp evaluation dùng một LLM (gọi là "judge") để chấm chất lượng output do một LLM app khác sinh ra. Judge nhận input, output và một rubric chấm điểm, rồi trả về score kèm reasoning giải thích. Score có thể là numeric (thang liên tục như helpfulness 0–1), categorical (nhãn rời như `correct`/`incorrect`) hoặc boolean (quyết định nhị phân). Evaluator được dựng trong Langfuse UI — chọn evaluator có sẵn từ catalog (Langfuse và đối tác như Ragas: Hallucination, Toxicity, Helpfulness…) hoặc tự viết prompt với biến `{{variables}}`. Judge model phải qua LLM Connection và **bắt buộc hỗ trợ structured output** để hệ thống parse được kết quả. Evaluator chạy trên Observations (khuyến nghị cho production, nhanh, chấm ở cấp thao tác) hoặc Experiments; bước cấu hình gồm filter, sampling %, và map biến prompt sang trường dữ liệu thật.

**!Note:** Ba chỗ chạy trơn nhưng âm thầm sai kết quả:
- Sampling áp **theo từng evaluator**, mỗi cái bốc mẫu ngẫu nhiên riêng. Hai evaluator cùng đặt 5% sẽ chấm hai tập con khác nhau. Muốn chúng chấm cùng một tập, phải để sampling 100% và filter giống hệt, hoặc tự quyết định sampling trong app rồi gắn tag cho evaluator lọc theo.
- Filter observation theo thuộc tính cấp trace (`userId`, `sessionId`, `tags`, `metadata`, `traceName`) đòi hỏi gọi `propagate_attributes()` trong code instrumentation. Nếu không propagate, observation sẽ không được evaluator match — không sinh score nào mà không báo lỗi.
- Trace-level evaluators đã **deprecated** (dựa trên data model trace-centric cũ); mốc gỡ bỏ sẽ công bố cùng Langfuse v4.

**Vai trò.** Chấm tự động ở quy mô lớn cho các khía cạnh cần phán đoán ngữ nghĩa hoặc theo rubric — helpfulness, toxicity, relevance, faithfulness của RAG — nơi model bắt được sắc thái mà heuristic đơn giản bỏ sót.

**Ví dụ.** Một RAG agent hỗ trợ khách: đặt một evaluator target observation retrieval để chấm relevance của tài liệu lấy về, và một evaluator khác target observation LLM generation cuối để chấm faithfulness của câu trả lời so với context; cả hai chạy ở sampling 5% để giữ chi phí judge trong ngưỡng.

Chi tiết cấu hình: https://langfuse.com/docs/evaluation/evaluation-methods/llm-as-a-judge

## 2. Code evaluators

**Khái niệm.** Cơ chế chạy logic Python hoặc TypeScript xác định (deterministic) ngay trong Langfuse và trả về một hoặc nhiều score. Mỗi evaluator expose hàm `evaluate(ctx)`; Langfuse truyền vào một `EvaluationContext` (chứa `observation.input`, `output`, `metadata`, `tool_calls`, và `experiment` nếu chạy trên experiment) và nhận lại `EvaluationResult` gồm danh sách score. Chạy trên Observations hoặc Experiments. Runtime bị siết chặt: chỉ dùng standard library (không package bên thứ ba), không truy cập mạng, phải xong trong 2 giây, source dưới 256 KB, và bắt buộc trả về ít nhất một score. Yêu cầu SDK nền OTel: Python v3+ hoặc JS/TS v4+.

**!Note:** Mạng bị chặn hoàn toàn — một request mạng vô tình để lại sẽ hiện ra dưới dạng **timeout error** chứ không phải lỗi mạng rõ ràng, dễ chẩn đoán nhầm. Ngoài ra `ctx.experiment` chỉ tồn tại khi evaluator chạy trên experiment; với evaluator live observation nó là `None` (Python) / `undefined` (TS), nên code phải tự xử lý nhánh này, nếu không sẽ lỗi khi chạy production.

**Vai trò.** Các kiểm tra khách quan, có đáp án đúng/sai rõ ràng — exact match, regex, JSON parse được không, schema validation, keyword, kiểm tra tool call, business rule — nơi code đáng tin hơn phán đoán của model.

**Ví dụ.** Kiểm tra output cuối của LLM có parse được thành JSON hợp lệ trên toàn bộ traffic production; hoặc trong một experiment, đối chiếu output với `item_expected_output` để trả boolean exact-match qua hai phiên bản prompt trên cùng dataset câu hỏi hỗ trợ.

Chi tiết cấu hình: https://langfuse.com/docs/evaluation/evaluation-methods/code-evaluators

## 3. Scores via API/SDK

**Khái niệm.** Cách đẩy score do chính app, pipeline hoặc CI job của ta tự tính vào Langfuse qua SDK/API, gắn lên trace, observation, session hoặc dataset run. Bốn kiểu: Numeric, Categorical, Boolean, Text. Điểm phân biệt với code evaluators: logic chấm chạy trong hạ tầng của ta, Langfuse chỉ nhận kết quả. Trace/observation score bắt buộc có `trace_id`, `observation_id` tùy chọn (nếu gắn vào observation thì phải đưa cả hai). Có `@langfuse/browser` để gửi score từ frontend (thumbs up/down, star rating) — chỉ cần public key, gửi ngay, không cần `flush()`.

**!Note:** Cơ chế định danh score dễ tạo bản trùng ngoài ý muốn. Một score được định danh bởi ba trường — `id`, `name`, và `timestamp` ở mức ngày. Score mới **chỉ ghi đè** khi cả ba khớp; cùng `id` nhưng khác `name` sẽ tạo thêm một score chứ không thay thế. Muốn cập nhật thay vì nhân bản, phải đặt `id` ổn định làm idempotency key ngay từ lần tạo đầu và giữ nguyên `name` + `timestamp`. Không được gửi partial update (chỉ field thay đổi) — cơ chế merge đó chỉ áp trong cửa sổ ngắn sau khi tạo, đã deprecated và sẽ bị gỡ; luôn gửi score đầy đủ.

**Vai trò.** Khi việc tính score nằm ngoài Langfuse — pipeline evaluation riêng, guardrail, hay tín hiệu người dùng thật — rồi đưa kết quả về Langfuse để tổng hợp cùng các score khác.

**Ví dụ.** Frontend gắn nút thumbs up/down; mỗi lượt bấm gọi browser SDK ingest một boolean score `user-feedback` (1/0) lên trace tương ứng, dùng `id` dạng `user-feedback-{traceId}` làm idempotency key để một trace chỉ giữ một điểm feedback mới nhất.

Chi tiết cấu hình: https://langfuse.com/docs/evaluation/evaluation-methods/scores-via-sdk

## 4. Scores via UI

**Khái niệm.** Cách chấm tay trực tiếp trên một trace, session hoặc observation qua form `Annotate` trong UI. Điều kiện: đã có ít nhất một Score Config định nghĩa các dimension chấm. Luồng: mở `Annotate` → chọn score config → đặt giá trị → thêm comment (tùy chọn); score hiện ở tab `Scores` của item. Chấm được cả trên experiment compare view, nơi input/output và các score tự động vẫn hiển thị đầy đủ trong lúc review, và metric tổng cập nhật theo mỗi điểm vừa thêm.

**Vai trò.** Cho nhiều người trong nhóm review tay để tạo baseline người — mốc benchmark hiệu chỉnh các score tự động và curate dataset chất lượng cao từ log production.

**Ví dụ.** Nhóm QA mở từng trace production của một chatbot, chấm dimension `accuracy` theo score config chung; tập điểm người này về sau dùng làm chuẩn để calibrate evaluator LLM-as-a-Judge.

Chi tiết cấu hình: https://langfuse.com/docs/evaluation/evaluation-methods/scores-via-ui

## 5. Annotation Queues

**Khái niệm.** Công cụ workflow tổ chức việc chấm tay ở mục 4 thành luồng phân công cho domain expert. Ta tạo queue gắn với một hoặc nhiều Score Config, nạp trace/observation/session vào (theo lô qua checkbox + `Add to queue`, hoặc từng item qua dropdown `Annotate`), rồi người review xử lý tuần tự: mỗi item hiện một task, chấm các dimension đã định, bấm `Complete + next`. Toàn bộ thao tác điều khiển được bằng bàn phím (mũi tên chuyển item, số chọn nhãn categorical/boolean, `Cmd/Ctrl + Enter` hoàn tất). Quản lý queue được qua API để scale và tự động hóa.

**Vai trò.** Khi cần review có tổ chức trên batch lớn — phân người, chấm nhất quán theo config, thêm corrected output (output đáng ra model phải sinh), và hiệu chỉnh LLM-as-a-Judge bằng annotation của người.

**Ví dụ.** Gom 200 trace của một agent hỗ trợ khách vào một queue, gán cho ba chuyên gia; mỗi người chấm lần lượt các dimension đã định qua phím tắt mà không rời bàn phím.

Chi tiết cấu hình: https://langfuse.com/docs/evaluation/evaluation-methods/annotation-queues

## Tham chiếu chéo

**Score Config là nền chung** của ba phương pháp có tính người/enforcement: Scores via UI và Annotation Queues bắt buộc có score config trước khi chấm; Scores via API/SDK dùng score config (qua `config_id`) để validate giá trị. Nội dung chi tiết về Score Config, score types và data model thuộc file scores/data-model, không lặp ở đây.

**Target Observations vs Experiments** là trục chung của LLM-as-a-Judge và Code evaluators: cùng khái niệm target, cùng chịu chi phối của filter và mapping. Riêng ràng buộc **sampling áp theo từng evaluator** (mục 1) chỉ đúng cho hai phương pháp Langfuse tự chạy này, không liên quan tới ba phương pháp còn lại.