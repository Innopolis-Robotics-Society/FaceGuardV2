# Roadmap - FaceGuardV2

**Product Goal:** Face recognition access control system on Raspberry Pi 5
with local user registration and access logging.

---

## Sprint 3: Core Authentication & Emulation
**Dates:** June 15 – June 21, 2026
**Milestone:** [Sprint 3](link-to-milestone)

**Goal:** Build the local database and a visual emulation of the door lock
so the auth logic can be tested without physical hardware.

**Planned items:**
- [US-002 User Registration](#issue) - register users via face vectors
- [US-007 UI Emulation](#issue) - emulate servo state on x86 laptop
- [#16 Database Schema](#issue) - profiles and embeddings tables

---

## Sprint 4: Hardware Integration
**Dates:** June 22 – June 28, 2026
**Milestone:** [Sprint 4](link-to-milestone)

**Goal:** Move from emulation to real execution on Raspberry Pi 4 with a
physical servo motor on GPIO pins.

**Planned items:**
- [US-001 Door Unlocking](#issue) - unlock on successful recognition
- [US-006 Servo Control](#issue) - motor rotation and auto-return
- [#25 GPIO Setup](#issue) - hardware control libraries for Pi 4

---

## Sprint 5: Security & Metrics
**Dates:** June 29 – July 5, 2026
**Milestone:** [Sprint 5](link-to-milestone)

**Goal:** Harden the system against spoofing attacks and tune the
recognition threshold using precision/recall analysis.

**Planned items:**
- [US-008 Pipeline Evaluation](#issue) - precision/recall on real datasets
- [US-010 Access Logging](#issue) - log confidence, lighting, mask flags
- [US-011 Strict Lock Policy](#issue) - reject low-confidence attempts
