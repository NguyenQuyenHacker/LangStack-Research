# Git Cheatsheet

> Tra nhanh khi làm việc. Phần lệnh nào chưa dùng đến thì bỏ qua, đừng cố học thuộc hết.

---

## 0. Khái niệm nền — hiểu cái này thì lệnh nào cũng dễ

Git có **4 vùng chứa code**. Mọi lệnh chỉ là di chuyển code giữa 4 vùng này:

```
Working Directory  →  Staging Area  →  Local Repository  →  Remote Repository
   (file đang sửa)      (đã git add)      (đã git commit)      (đã git push)
```

| Vùng | Là gì | Lệnh đưa vào |
|---|---|---|
| Working Directory | Thư mục thật trên máy, file bạn đang gõ | (sửa file) |
| Staging Area (Index) | Giỏ hàng — chọn file nào sẽ vào commit tới | `git add` |
| Local Repository | Lịch sử commit nằm trong thư mục `.git` | `git commit` |
| Remote Repository | Server GitHub/GitLab | `git push` |

Vài từ hay gặp:

- **HEAD** — con trỏ chỉ vào commit hiện tại bạn đang đứng
- **HEAD~1** — commit trước HEAD 1 bước, `HEAD~3` là lùi 3 bước
- **origin** — tên mặc định của remote, không có gì thiêng liêng, đổi tên được
- **main / master** — tên nhánh chính, `main` là chuẩn mới, `master` là tên cũ
- **commit hash** — mã định danh commit, dạng `a3f5b21...`, gõ 7 ký tự đầu là đủ

---

## 1. Khởi tạo & cấu hình

```bash
git init                          # biến thư mục hiện tại thành repo git
git clone <url>                   # tải repo từ server về máy
git clone <url> <tên-thư-mục>     # tải về và đặt tên thư mục khác
git clone --depth 1 <url>         # chỉ lấy commit mới nhất, repo nặng thì nhanh hơn nhiều
```

Cấu hình danh tính — bắt buộc làm 1 lần sau khi cài Git:

```bash
git config --global user.name "Nguyen Ngoc Anh"
git config --global user.email "email@example.com"
git config --global init.defaultBranch main     # repo mới mặc định nhánh main
git config --global core.editor "code --wait"   # dùng VS Code làm editor
git config --list                               # xem toàn bộ cấu hình hiện tại
```

Bỏ `--global` để chỉ áp dụng cho repo hiện tại — hữu ích khi máy dùng chung cho project công ty và project cá nhân với 2 email khác nhau.

Trên Windows nên bật để tránh lỗi xuống dòng CRLF/LF:

```bash
git config --global core.autocrlf true      # Windows
git config --global core.autocrlf input     # macOS / Linux
```

---

## 2. Xem tình hình — gõ nhiều nhất trong ngày

```bash
git status                  # file nào đã sửa, đã add, chưa add
git status -s               # bản rút gọn, dễ nhìn hơn khi nhiều file

git diff                    # nội dung đã sửa nhưng CHƯA add
git diff --staged           # nội dung đã add, chuẩn bị commit
git diff HEAD               # tất cả thay đổi so với commit gần nhất
git diff <nhánh-A> <nhánh-B>    # so sánh 2 nhánh
git diff --stat             # chỉ liệt kê tên file + số dòng đổi, không xem chi tiết
```

Ký hiệu trong `git status -s`: cột 1 là staging, cột 2 là working directory.
`M` = modified, `A` = added, `D` = deleted, `??` = file mới chưa được theo dõi.

Xem lịch sử:

```bash
git log                              # đầy đủ, dài
git log --oneline -10                # 10 commit gần nhất, mỗi commit 1 dòng
git log --oneline --graph --all      # xem cây nhánh — lệnh đáng nhớ nhất
git log -p <file>                    # lịch sử thay đổi của riêng 1 file
git log --author="Ngoc Anh"          # lọc theo người commit
git log --since="2 weeks ago"        # lọc theo thời gian
git show <hash>                      # xem chi tiết 1 commit cụ thể
git blame <file>                     # mỗi dòng code do ai viết, ở commit nào
```

---

## 3. Lưu code

```bash
git add <file>              # chọn file cụ thể
git add .                   # tất cả file trong thư mục hiện tại trở xuống
git add -A                  # tất cả file trong toàn repo
git add -p                  # duyệt từng đoạn thay đổi, chọn add hay không — rất hay
git add *.py                # theo pattern

git commit -m "nội dung"
git commit -am "nội dung"   # add + commit gộp, CHỈ với file đã từng được theo dõi
git commit                  # mở editor để viết message nhiều dòng
```

Cách viết commit message thường dùng trong team (Conventional Commits):

```
feat: thêm API tra cứu số dư tài khoản
fix: sửa lỗi timeout khi gọi LangGraph agent
docs: cập nhật README hướng dẫn cài đặt
refactor: tách logic chunking ra module riêng
chore: nâng version langchain lên 0.3.2
test: thêm unit test cho retriever
```

Dòng đầu dưới 50 ký tự, viết ở thì hiện tại ("thêm" chứ không phải "đã thêm").

---

## 4. Nhánh (branch)

```bash
git branch                        # xem nhánh local
git branch -a                     # xem cả nhánh remote
git branch -v                     # kèm commit gần nhất của mỗi nhánh

git switch <nhánh>                # chuyển nhánh          (lệnh mới)
git switch -c <nhánh-mới>         # tạo nhánh mới + chuyển sang luôn
git switch -                      # quay lại nhánh vừa rời khỏi

git checkout <nhánh>              # lệnh cũ, tương đương git switch
git checkout -b <nhánh-mới>       # lệnh cũ, tương đương git switch -c

git branch -d <nhánh>             # xóa nhánh đã merge
git branch -D <nhánh>             # xóa cưỡng chế dù chưa merge
git branch -m <tên-mới>           # đổi tên nhánh đang đứng
git push origin --delete <nhánh>  # xóa nhánh trên server
```

`checkout` làm quá nhiều việc (chuyển nhánh, khôi phục file, tách HEAD) nên Git tách ra thành `switch` (chuyển nhánh) và `restore` (khôi phục file). Dùng cặp mới cho đỡ nhầm.

### Gộp nhánh

```bash
git merge <nhánh>           # gộp nhánh kia VÀO nhánh đang đứng
git merge --no-ff <nhánh>   # luôn tạo commit merge, giữ dấu vết nhánh
git merge --abort           # hủy merge khi đang conflict rối quá
```

Quy trình đúng khi merge `feature` vào `main`:

```bash
git switch main
git pull                    # cập nhật main mới nhất
git merge feature
git push
```

### Rebase — làm lịch sử thẳng hàng

```bash
git rebase main             # chuyển các commit của nhánh hiện tại lên đầu main
git rebase --continue       # tiếp tục sau khi xử lý xong conflict
git rebase --abort          # hủy, quay về trạng thái trước rebase
git rebase -i HEAD~5        # interactive: gộp/sửa/xóa 5 commit gần nhất
```

**Nguyên tắc vàng:** chỉ rebase nhánh riêng của mình, chưa ai khác dùng. Rebase nhánh chung là viết lại lịch sử, cả team sẽ vỡ.

---

## 5. Xử lý conflict

Khi merge/pull/rebase mà 2 bên cùng sửa 1 chỗ, Git dừng lại và chèn vào file:

```
<<<<<<< HEAD
code của nhánh bạn đang đứng
=======
code của nhánh được gộp vào
>>>>>>> feature/abc
```

Cách xử lý:

1. `git status` — xem file nào conflict
2. Mở file, xóa 3 dòng ký hiệu `<<<<<<<`, `=======`, `>>>>>>>`, giữ lại nội dung đúng
3. `git add <file>` — báo Git đã xử lý xong
4. `git commit` (nếu merge) hoặc `git rebase --continue` (nếu rebase)

Muốn lấy nguyên một bên, khỏi sửa tay:

```bash
git checkout --ours <file>      # giữ bản của nhánh đang đứng
git checkout --theirs <file>    # giữ bản của nhánh đang gộp vào
git add <file>
```

---

## 6. Đồng bộ với server

```bash
git fetch                        # tải thông tin mới về, KHÔNG đụng code local
git fetch --all                  # fetch tất cả remote
git fetch --prune                # dọn các nhánh remote đã bị xóa trên server

git pull                         # = fetch + merge
git pull --rebase                # = fetch + rebase, lịch sử sạch hơn

git push                         # đẩy commit lên
git push -u origin <nhánh>       # lần đầu đẩy nhánh mới, gắn liên kết theo dõi
git push --all                   # đẩy TẤT CẢ nhánh local
git push --tags                  # đẩy tag
git push --force-with-lease      # ghi đè server nhưng vẫn kiểm tra an toàn
git push --force                 # ghi đè thẳng — nguy hiểm, cân nhắc kỹ
```

`--force-with-lease` an toàn hơn `--force`: nó từ chối push nếu người khác vừa đẩy commit mới lên nhánh đó mà bạn chưa biết. Dùng cái này thay cho `--force` trong mọi trường hợp.

### Quản lý remote

```bash
git remote -v                          # xem danh sách remote
git remote add <tên> <url>             # thêm remote mới
git remote set-url <tên> <url>         # đổi URL của remote đã có
git remote set-url --push <tên> <url>  # đổi riêng URL push
git remote remove <tên>                # xóa remote
git remote rename <cũ> <mới>           # đổi tên remote
git remote show origin                 # xem chi tiết remote
```

Một remote có 2 URL riêng cho fetch và push. Mặc định chúng giống nhau nên `git remote -v` in 2 dòng trùng nhau.

Đẩy 1 repo lên 2 nơi cùng lúc (GitHub + GitLab):

```bash
git remote add gitlab <url-gitlab>
git push origin main        # lên GitHub
git push gitlab main        # lên GitLab
git push gitlab --all       # đẩy toàn bộ nhánh lên GitLab
```

---

## 7. Cứu hộ — lúc lỡ tay

### Chưa commit

```bash
git restore <file>                 # bỏ sửa đổi chưa add, quay về như cũ — MẤT code đã sửa
git restore .                      # bỏ toàn bộ sửa đổi chưa add
git restore --staged <file>        # bỏ add, giữ nguyên nội dung đã sửa
git restore --source=HEAD~2 <file> # lấy lại file từ commit 2 bước trước
```

### Đã commit nhưng CHƯA push

```bash
git commit --amend                 # sửa lại commit vừa tạo (nội dung hoặc message)
git commit --amend --no-edit       # thêm file vào commit vừa rồi, giữ nguyên message

git reset --soft HEAD~1            # hủy commit, giữ code + giữ staging
git reset --mixed HEAD~1           # hủy commit, giữ code, bỏ staging  (mặc định)
git reset --hard HEAD~1            # hủy commit + XÓA LUÔN CODE — cẩn thận
```

### Đã push lên nhánh chung

```bash
git revert <hash>                  # tạo commit mới đảo ngược commit cũ — an toàn
git revert <hash-cũ>..<hash-mới>   # revert một dải commit
```

Đã push rồi thì đừng `reset`, dùng `revert`. Reset viết lại lịch sử, người khác pull về sẽ vỡ.

### Cất tạm việc đang làm dở

```bash
git stash                       # cất tạm, thư mục trở về sạch sẽ
git stash -u                    # cất cả file mới chưa được theo dõi
git stash save "đang sửa RAG"   # cất kèm ghi chú
git stash list                  # xem danh sách đã cất
git stash pop                   # lấy lại cái mới nhất và xóa khỏi stash
git stash apply stash@{2}       # lấy lại cái thứ 2, vẫn giữ trong stash
git stash drop stash@{0}        # xóa 1 mục
git stash clear                 # xóa sạch stash
```

Tình huống điển hình: đang sửa dở nhánh A thì sếp bảo fix gấp nhánh B. `git stash` → `git switch B` → fix → `git switch A` → `git stash pop`.

### Phao cứu sinh cuối cùng

```bash
git reflog                      # nhật ký MỌI vị trí HEAD từng đứng, kể cả commit đã "mất"
git reset --hard <hash>         # nhảy về vị trí đó
```

`reflog` cứu được gần như mọi tai nạn: lỡ `reset --hard`, lỡ xóa nhánh, lỡ rebase hỏng. Git giữ commit "mồ côi" khoảng 30 ngày trước khi dọn. Chỉ có code **chưa từng commit** là mất thật.

---

## 8. Bỏ qua file — .gitignore

Tạo file tên `.gitignore` ở gốc repo:

```gitignore
# Môi trường & bí mật — QUAN TRỌNG NHẤT
.env
.env.*
*.key
*.pem
credentials.json

# Python
__pycache__/
*.pyc
venv/
.venv/
*.egg-info/

# Node
node_modules/
dist/
build/
.next/

# IDE & hệ điều hành
.vscode/
.idea/
.DS_Store
Thumbs.db

# Dữ liệu & model
*.log
*.sqlite3
*.pt
*.onnx
data/raw/
```

`.gitignore` chỉ có tác dụng với file **chưa từng** được commit. Nếu lỡ commit `.env` rồi thì:

```bash
git rm --cached .env        # bỏ khỏi git, GIỮ file trên máy
git commit -m "chore: bỏ .env khỏi repo"
```

Nhưng file cũ vẫn nằm trong lịch sử — ai đọc `git log` vẫn thấy nội dung. **Phải đổi ngay toàn bộ mật khẩu / API key đã lộ.** Muốn xóa sạch khỏi lịch sử cần công cụ riêng như `git filter-repo` hoặc BFG Repo-Cleaner, và phải force push cả repo.

---

## 9. Tag — đánh dấu phiên bản

```bash
git tag                                  # liệt kê tag
git tag v1.0.0                           # tag nhẹ
git tag -a v1.0.0 -m "Bản phát hành đầu" # tag có chú thích — nên dùng cái này
git tag -a v1.0.0 <hash>                 # tag cho commit cũ
git push origin v1.0.0                   # đẩy 1 tag
git push --tags                          # đẩy tất cả tag
git tag -d v1.0.0                        # xóa tag local
git push origin --delete v1.0.0          # xóa tag trên server
```

---

## 10. Lệnh nâng cao thỉnh thoảng cần

```bash
git cherry-pick <hash>          # lấy 1 commit từ nhánh khác về nhánh hiện tại
git bisect start                # nhị phân tìm commit gây bug
git clean -fd                   # xóa file/thư mục chưa được theo dõi — không hoàn tác được
git clean -n                    # xem trước clean sẽ xóa gì
git worktree add ../thư-mục <nhánh>   # mở 2 nhánh cùng lúc ở 2 thư mục khác nhau
git archive -o code.zip HEAD    # xuất code ra zip, không kèm .git
```

---

## 11. Quy trình làm việc chuẩn trong team

```bash
# 1. Cập nhật nhánh chính
git switch main
git pull

# 2. Tạo nhánh cho việc mới
git switch -c feat/them-api-tra-cuu

# 3. Làm việc, commit nhiều lần nhỏ
git add .
git commit -m "feat: thêm endpoint tra cứu"

# 4. Đẩy lên server
git push -u origin feat/them-api-tra-cuu

# 5. Mở Pull Request (GitHub) / Merge Request (GitLab) trên web
# 6. Review xong, merge trên web
# 7. Dọn dẹp
git switch main
git pull
git branch -d feat/them-api-tra-cuu
```

Đừng commit thẳng vào `main` của project chung. Luôn tạo nhánh, mở MR/PR.

---

## 12. Đặt tên viết tắt cho lệnh hay dùng

```bash
git config --global alias.st status
git config --global alias.co checkout
git config --global alias.br branch
git config --global alias.cm "commit -m"
git config --global alias.lg "log --oneline --graph --all --decorate"
git config --global alias.last "log -1 HEAD"
git config --global alias.unstage "restore --staged"
```

Sau đó gõ `git st`, `git lg` thay cho lệnh dài.

---

## Ba điều đáng nhớ hơn cả toàn bộ file này

**`git status` trước mọi thao tác.** Git luôn in gợi ý lệnh tiếp theo ngay trong output — đọc là ra cách xử lý, không cần tra cứu.

**`--hard`, `--force`, `clean` là những lệnh có thể làm mất code vĩnh viễn.** Ngoài chúng ra, mọi thứ đã commit đều lấy lại được bằng `git reflog`.

**Đã push lên nhánh chung thì đừng viết lại lịch sử.** Không `reset`, không `rebase`, không `--force`. Dùng `revert`.