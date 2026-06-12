## US-01: Automatic Door Unlocking

**Requirement status:** Active
**MoSCoW priority:** Must Have

As a lab worker,
I want the door to unlock automatically when my face is recognized,
so that I can enter the building without carrying access cards or remembering passwords.

### Notes and constraints

The pipeline must process the camera stream in real time to ensure low entry latency for users.

---

## US-02: User Registration

**Requirement status:** Active
**MoSCoW priority:** Must Have

As a system administrator,
I want to register new users by capturing their face and saving them to the database,
so that the system can recognize people.

### Notes and constraints

Registration should capture several different face angles to improve the accuracy of face embeddings in various conditions.

---

## US-03: Temporary Visitor Access

**Requirement status:** Active
**MoSCoW priority:** Should Have

As a visitor,
I want the system to register me so that the system gives temporary access,
so that I can have access to the lab.

### Notes and constraints

Requires an option or logic in the database to automatically expire or manually revoke visitor access privileges after a certain period.

---

## US-04: Multi-Architecture Docker Packaging

**Requirement status:** Active
**MoSCoW priority:** Could Have

As a security manager,
I want the entire system packaged in Docker and runnable on ARM and x86 architectures,
so that development, debugging, and production deployment are consistent across platforms.

### Notes and constraints

The Docker setup must support building for both Raspberry Pi 5 (ARM) and regular laptop development environments (x86).

---

## US-05: Graphical User Interface Feedback

**Requirement status:** Active
**MoSCoW priority:** Could Have

As a user approaching the door,
I want the UI to show some information when recognized, or "Unknown," and some technical information,
so that I immediately know whether the system has identified me and if the door should open.

### Notes and constraints

The interface needs to cleanly display the real-time camera frame, identified name (or fallback text), and the system confidence metric.

---

## US-06: Physical Lock Servo Feedback

**Requirement status:** Active
**MoSCoW priority:** Must Have

As a lab worker,
I want the physical servo motor to rotate when my face is successfully recognized and then return to its original position,
so that I receive clear physical feedback that the door is unlocked and I can push it open.

### Notes and constraints

The hardware must safely interface via the Raspberry Pi 5 GPIO pins and automatically reset the lock status after a brief timeout.

---

## US-07: Cross-Platform Servo Emulation

**Requirement status:** Active
**MoSCoW priority:** Must Have

As a developer,
I want the user interface to visually emulate the servo motor's rotation when running the system on a laptop (x86),
so that I can thoroughly debug and test the locking logic without needing access to the physical hardware.

### Notes and constraints

The graphical representation on x86 must accurately replicate the states and timing of the physical ARM-based servo triggers.

---

## US-08: Data-Driven Threshold Selection

**Requirement status:** Active
**MoSCoW priority:** Must Have

As an ML engineer,
I want to evaluate the face recognition pipeline on real dataset samples to calculate precision and recall curves,
so that I can choose an optimal decision threshold instead of guessing.

### Notes and constraints

The chosen threshold must balance security (minimizing false acceptances) with usability (minimizing false rejections) based on concrete metrics.

---

## US-09: Presentation Attack Protection

**Requirement status:** Active
**MoSCoW priority:** Could Have

As a security manager,
I want the system to perform a liveness detection check during the recognition process,
so that unauthorized individuals cannot spoof the system using printed photos or digital screens.

### Notes and constraints

This anti-spoofing feature is a bonus objective and must not significantly delay real-time face recognition execution speeds on the Raspberry Pi 5.

---

## US-10: Failure Mode Audit Logging

**Requirement status:** Active
**MoSCoW priority:** Should Have

As a security manager,
I want the system to log access attempts—including confidence scores and specific failure categories like poor lighting, masks, or glasses—
so that we can audit entry events and explicitly document where the technical boundaries of the system fail.

### Notes and constraints

Environmental and user constraints (poor lighting, glasses, masks, similar faces) are recognized limitations of the current technology and must be clearly audited rather than classified as software defects.