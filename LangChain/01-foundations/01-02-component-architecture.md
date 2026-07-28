---
title: Kiến trúc thành phần
doc_source: https://docs.langchain.com/oss/python/langchain/component-architecture
accessed: 2026-07-25
lc_version: unknown
status: draft
lab: 
---

# KIẾN TRÚC THÀNH PHẦN

[Tài liệu tham khảo](https://docs.langchain.com/oss/python/langchain/component-architecture)



## 1. CÁC NHÓM THÀNH PHẦN

| Nhóm | Vai trò | Thành phần chính |
|---|---|---|
| **Models** | Suy luận và sinh nội dung | Chat models, LLMs, Embedding models |
| **Tools** | Năng lực bên ngoài | API, cơ sở dữ liệu |
| **Agents** | Điều phối và ra quyết định | ReAct agent, tool calling agent |
| **Memory** | Giữ ngữ cảnh | Lịch sử tin nhắn, trạng thái tự định nghĩa |
| **Retrievers** | Truy cập thông tin | Vector retriever, web retriever |
| **Document processing** | Nạp dữ liệu | Loaders, splitters, transformers |
| **Vector Stores** | Tìm theo ngữ nghĩa | Chroma, Pinecone, FAISS |

---

## 2. CÁC KIẾN TRÚC THƯỜNG GẶP

### 2.1. RAG — Retrieval-Augmented Generation

Trả lời dựa trên tài liệu của mình thay vì dựa vào kiến thức có sẵn của model.

![markdown](../assets/diagrams/Screenshot%202026-07-22%20153253.png)

Câu hỏi đi theo hai đường: một đường đi tìm tài liệu, một đường đi thẳng tới model. Model nhận cả câu hỏi lẫn tài liệu tìm được rồi mới trả lời.

### 2.2. Agent với tool

![markdown](../assets/diagrams/Screenshot%202026-07-22%20153305.png)

Mũi tên từ **Kết quả** quay ngược về **Agent** chính là vòng lặp. Agent chạy bao nhiêu vòng là do model quyết, không do người viết code định trước.

### 2.3. Hệ nhiều agent

![markdown](../assets/diagrams/Screenshot%202026-07-22%20153318.png)

Một agent giám sát chia việc cho các agent chuyên trách, thu kết quả về rồi tổng hợp lại.

---

## 3. GHI CHÚ

Việc ứng dụng của bạn có bao nhiêu tầng hay không phụ thuộc vào nhu cầu của nó.

- Agent chỉ gọi tool thì bỏ hẳn tầng 1–3;
- RAG thuần thì không cần tầng 5.

