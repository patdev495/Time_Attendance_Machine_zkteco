# Project State: Time Attendance Machine

## Current Milestone
- **Name**: v8.1 — Kiosk, Live Mode & Deployments (Current Codebase: v8.1.3)
- **Status**: Completed
- **Progress**: 100%

## Active Phase
- **Phase**: None
- **Goal**: Project exploration and context alignment.

## Accumulated Context

### Project Vision
Refactor completed (v2.0). Now focusing on professionalizing the application with full internationalization (i18n) support for English, Vietnamese, and Chinese.

### Architecture
- Feature-based vertical slices in both backend and frontend.
- `EmployeeLocalRegistry` unifies Excel, Machine, and Log-only sources.
- `i18n` setup exists in `frontend/src/i18n`.

### Key Constraints
- Windows OS deployment.
- MSSQL 2008 compatibility.
- Hardware dependency on ZKTeco (PyZK).
- `uv pip` for Python packages.
- **i18n**: English is the default and fallback.

### Roadmap Evolution
- v1.x: Backend modernization.
- v2.0: Feature-based architecture refactor (Completed 2026-04-10).
- v3.0: Comprehensive Multi-language Support (Started 2026-04-10).
- Phase 13 added: Điều chỉnh cách tính công và tăng ca.

### Quick Tasks Completed

| # | Description | Date | Commit | Directory |
|---|-------------|------|--------|-----------|
| 260505-i86 | Triển khai chức năng tự động cập nhật giờ của các máy chấm công, nghiên cứu xem sdk này có hỗ trợ không | 2026-05-05 | 630b965 | [260505-i86-tri-n-khai-ch-c-n-ng-t-ng-c-p-nh-t-gi-c-](./quick/260505-i86-tri-n-khai-ch-c-n-ng-t-ng-c-p-nh-t-gi-c-/) |

---
*Last updated: 2026-05-05*
