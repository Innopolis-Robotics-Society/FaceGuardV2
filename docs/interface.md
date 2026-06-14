# FaceGuard — Interface Documentation

## Overview

FaceGuard has two interfaces:

| Interface | Type | User | Status |
|-----------|------|------|--------|
| **Live Display** | Graphical (OpenCV window) | All users (employees, guests) | Implemented in MVP v0 |
| **Admin CLI** | Command-line | System administrators | Planned for production |

---

## 1. Live Display (OpenCV Window)

Real-time camera feed shown during system operation. No user input required — the user simply stands in front of the camera.

### States

#### 1.1 Locked (no face detected)
- Solid red border around frame
- Text: `LOCKED`
- No action required; system waits

```
┌─────────────────────┐
│  [Camera feed]      │
│                     │
│      LOCKED         │
│                     │
└─────────────────────┘
      (red border)
```

*[Screenshot: locked_state.png]*

#### 1.2 Scanning (face detected, processing)
- Yellow border
- Text: `Scanning...`
- Progress indicator (dots cycling)

```
┌─────────────────────┐
│  [Camera feed]      │
│   ┌─────────┐       │
│   │  face   │       │
│   └─────────┘       │
│    Scanning...      │
│                     │
└─────────────────────┘
     (yellow border)
```

*[Screenshot: scanning_state.png]*

#### 1.3 Recognized (known user)
- Green border
- Text: `{name} — {score:.2f}`
- Large `UNLOCKED` banner for 0.5s
- Servo rotates (emulated as banner on laptop, real hardware on Pi)

```
┌─────────────────────┐
│  [Camera feed]      │
│   ┌─────────┐       │
│   │  face   │       │
│   └─────────┘       │
│   Vasya — 0.82      │
│    UNLOCKED         │
│                     │
└─────────────────────┘
     (green border)
```

*[Screenshot: recognized_state.png]*

#### 1.4 Unknown (face detected, not in database)
- Orange border
- Text: `Unknown — {score:.2f}`
- Door remains locked

```
┌─────────────────────┐
│  [Camera feed]      │
│   ┌─────────┐       │
│   │  face   │       │
│   └─────────┘       │
│   Unknown — 0.34    │
│                     │
└─────────────────────┘
    (orange border)
```

*[Screenshot: unknown_state.png]*

#### 1.5 Error (camera failure, model load error)
- Flashing red border
- Text: `Error: {message}`
- System halts or retries

```
┌─────────────────────┐
│  [Camera feed]      │
│                     │
│  Error: No camera   │
│                     │
└─────────────────────┘
  (flashing red border)
```


---

## 2. Admin CLI

Planned interface for user management, registration, and system maintenance. Not implemented in MVP v0; documented for production deployment.

### Commands

#### `register <name>`
Register a new user from camera.

```
$ faceguard register "Ivan Petrov"
Position face in frame. Capturing 5 samples...
[#####] Done.
User "Ivan Petrov" registered. Embedding saved.
```

#### `remove <name>`
Remove user or guest.

```
$ faceguard remove "Ivan Petrov"
User removed.
```

#### `list`
Show all active users and guests.

```
$ faceguard list

PERMANENT USERS:
  Ivan Petrov      | since 2026-06-01
  Maria Sidorova   | since 2026-06-03

TEMPORARY GUESTS:
  Courier #5       | expires 2026-06-12 18:00 | added by admin_dmitry
  Visitor Ivanov   | expires 2026-06-12 15:00 | added by admin_dmitry
```

#### `add-guest <name> --hours <N>`
Add temporary access.

```
$ faceguard add-guest "Courier #5" --hours 8
Guest registered. Expires: 2026-06-12 18:00
```

#### `logs [--today] [--user <name>]`
View access logs.

```
$ faceguard logs --today
14:32 | Vasya          | user  | score 0.82 | OK
14:45 | Unknown        | -     | score 0.34 | DENIED
15:01 | Visitor Ivanov | guest | score 0.71 | OK
15:23 | Courier #5     | guest | score 0.69 | OK
```

#### `status`
System health check.

```
$ faceguard status
Camera: OK
Model: buffalo_m loaded
Database: 12 users, 3 active guests
Uptime: 4h 23m
Last recognition: 15:23 (Courier #5)
```

#### `threshold <value>`
Update recognition threshold (runtime).

```
$ faceguard threshold 0.65
Threshold updated: 0.60 → 0.65
```

### Error Examples

```
$ faceguard register "Vasya"
Error: User "Vasya" already exists. Use `remove` first.

$ faceguard add-guest "Temp" --hours 48
Error: Max guest duration is 24 hours.

$ faceguard remove "Nonexistent"
Error: User not found.
```

---

## 3. Interface Comparison

| Aspect | Live Display | Admin CLI |
|--------|-------------|-----------|
| **User** | Employee, guest | System admin |
| **Input** | None (passive) | Typed commands |
| **Output** | Visual feedback | Text tables |
| **Location** | Raspberry Pi + camera | SSH / local terminal |
| **Authentication** | Biometric (face) | SSH key / system user |
| **MVP v0** | Implemented | Documented, not implemented |



