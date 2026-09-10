# Product

<!-- impeccable:product-schema 1 -->

## Platform

web

## Users

**Operators** — HR personnel, factory floor supervisors, or administrative staff at a manufacturing or enterprise facility in Vietnam. They use this dashboard at a desktop workstation (typically 1920×1080 or laptop at 1366×768) during working hours to oversee employee attendance, investigate anomalies, sync data from biometric terminals, and export reports. The Meal Kiosk view is used on a dedicated screen (kiosk device) in the canteen.

## Product Purpose

A dashboard that synchronizes biometric attendance data from ZKTeco hardware terminals, processes and presents Raw Logs and Daily Summaries, manages employee records and shift definitions, and tracks canteen meal consumption. Operators use it to answer "who was late, who worked overtime, who skipped a meal" — all in one place.

## Positioning

Purpose-built for Vietnamese factories using ZKTeco ZK-protocol terminals. Direct connection to the hardware SDK means data is pulled without a middleware cloud. Shift-aware calculation (normal, rest, holiday overtime) combined with canteen meal tracking is the mechanism no generic attendance SaaS copies exactly.

## Operating Context

- Desktop workstation; wide viewport is the primary environment.
- Laptop screens at 1366×768 are common; a 0.75 zoom workaround is currently in the CSS.
- Data refreshed via manual sync or live WebSocket feed.
- Multiple biometric machines per facility (identified by IP address).
- Multilingual: Vietnamese primary, English and Chinese secondary.
- Canteen kiosk is a full-screen dedicated mode (no sidebar/header).

## Capabilities and Constraints

- **Raw Logs**: timestamped check-in/check-out events, filterable by employee, machine, date range. Live mode via WebSocket.
- **Daily Summary**: computed work hours, late/early/OT per employee per day, exportable to Excel.
- **Employees**: registry of employees across Excel-synced, machine-only, and log-only sources.
- **Machines**: ZKTeco terminal list, live/canteen toggle, reconnect action.
- **Shifts**: shift definition management (work windows, breaks, OT rules).
- **Meal Tracking / Kiosk**: full-screen kiosk for canteen pickup verification.
- Vue 3 + Vite frontend; FastAPI + SQLite backend; Docker-deployable.
- No authentication system currently.

## Brand Commitments

No formal brand identity. Product name: **Time Attendance Machine** (internal tool). Domain language per CONTEXT.md must be used: Raw Log, Daily Summary, Shift Definition, Meal Tracking, Attendance Machine, Employee.

## Evidence on Hand

- Working codebase with all features functional.
- i18n in Vietnamese, English, Chinese.
- ZKTeco hardware integration.

## Product Principles

1. **Operators first**: every interaction serves the person solving an attendance or payroll problem, not a passive reader.
2. **Data density earns its room**: tables and metrics are the product; chrome is infrastructure.
3. **Live and historical coexist**: the same surface switches from real-time feed to paginated history without a jarring context shift.
4. **Vietnamese workplace conventions**: date formats, language defaults, and shift terminology match local practice.
5. **Hardware-integrated**: machine status and connectivity are first-class, not buried settings.
