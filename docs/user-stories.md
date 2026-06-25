# Product Backlog — User Stories

## 1. Requirement Index Table

| ID | Short title | MoSCoW priority | Issue | Requirement status | Work Status |
|---|---|---|---|---|---|
| US-001 | Automatic door unlocking | Must Have | [#7](https://github.com/Innopolis-Robotics-Society/FaceGuardV2/issues/7) | Active | To Do | 
| US-002 | Register new users to DB | Must Have | [#8](https://github.com/Innopolis-Robotics-Society/FaceGuardV2/issues/8) | Active | In Progress |
| US-003 | Visitor temporary access | — | — | Removed | — |
| US-004 | Docker multi-arch package | Could Have | [#9](https://github.com/Innopolis-Robotics-Society/FaceGuardV2/issues/9) | Active | To Do |
| US-005 | UI status & info display | Should Have | [#11](https://github.com/Innopolis-Robotics-Society/FaceGuardV2/issues/11) | Active | To Do |
| US-006 | Physical servo motor control | Must Have | [#13](https://github.com/Innopolis-Robotics-Society/FaceGuardV2/issues/13) | Active | To Do |
| US-007 | UI servo emulation on x86 | Must Have | [#12](https://github.com/Innopolis-Robotics-Society/FaceGuardV2/issues/12) | Active | Done |
| US-008 | Pipeline dataset evaluation | Must Have | [#14](https://github.com/Innopolis-Robotics-Society/FaceGuardV2/issues/14) | Active | To Do |
| US-009 | Liveness detection check | — | — | Removed | — | — |
| US-010 | Detailed access attempt logs | Should Have | [#16](https://github.com/Innopolis-Robotics-Society/FaceGuardV2/issues/16) | Active | To Do |
| US-011 | Lock door on low confidence | Must Have | [#11](https://github.com/Innopolis-Robotics-Society/FaceGuardV2/issues/17) | Active | To Do |
| US-012 | Evaluation quality report | Must Have | [#19](https://github.com/Innopolis-Robotics-Society/FaceGuardV2/issues/19) | Active | To Do |
| US-013 | Manage temporary access life | Must Have | [#20](https://github.com/Innopolis-Robotics-Society/FaceGuardV2/issues/20)| Active | To Do |
| US-014 | Proximity single-user focus | Should Have | [#22](https://github.com/Innopolis-Robotics-Society/FaceGuardV2/issues/22) | Active | To Do | — |
| US-015 | Hardware LED indicators | Should Have | [#23](https://github.com/Innopolis-Robotics-Society/FaceGuardV2/issues/23) | Active | To Do | — |

---

## 2. Active User Story Statements

**US-001 (Must Have)**
* **Statement:** As a lab worker, I want the door to unlock automatically when my face is recognized, so that I can enter the building without carrying access cards or remembering passwords.

**US-002 (Must Have)**
* **Statement:** As a system administrator, I want to register new users by capturing face and saving them to the database, so that the system can recognize people.

**US-004 (Could Have)**
* **Statement:** As a security manager, I want the entire system packaged in docker and runnable on arm and x86 arch's, so that development, debugging, and production deployment are consistent across platforms.

**US-005 (Should Have)**
* **Statement:** As a user approaching the door, I want the UI to show some information when recognized, or "Unknown," and some technical information, so that I immediately know whether the system has identified me and if the door should open.

**US-006 (Must Have)**
* **Statement:** As a lab worker, I want the physical servo motor to rotate when my face is successfully recognized and then return to its original position, so that I receive clear physical feedback that the door is unlocked and I can push it open.

**US-007 (Must Have)**
* **Statement:** As a developer, I want the user interface to visually emulate the servo motor's rotation when running the system on a laptop (x86), so that I can thoroughly debug and test the locking logic without needing access to the physical hardware.

**US-008 (Must Have)**
* **Statement:** As an ML engineer, I want to evaluate the face recognition pipeline on real dataset samples to calculate precision and recall curves, so that I can choose an optimal decision threshold instead of guessing.

**US-010 (Should Have)**
* **Statement:** As a security manager, I want the system to log access attempts — including confidence scores and specific failure categories like poor lighting, masks, or glasses — so that we can audit entry events and explicitly document where the technical boundaries of the system fail.

**US-011 (Must Have)**
* **Statement:** As a security manager, I want the door to stay locked when the user is unknown or confidence is too low, so that unauthorized people cannot enter the lab.

**US-012 (Must Have)**
* **Statement:** As an ML engineer, I want to see an evaluation report with precision, recall, F1-score, and the recommended threshold, so that I can understand the system quality and choose the best threshold.

**US-013 (Must Have)**
* **Statement:** As a system administrator, I want to set explicit expiration dates and times for user profiles with temporary privileges, so that their access tokens and recognition vectors are automatically invalidated by the database without manual review.

**US-014 (Should Have)**
* **Statement:** As a user approaching the door in a crowd, I want the system camera to lock onto and evaluate only the single individual closest to the lens, so that background bystanders do not generate false matching logs or interfere with the unlock decision threshold.

**US-015 (Should Have)**
* **Statement:** As a lab worker, I want external green and red LED indicators driven by the GPIO pins to flash upon access decision, so that I have unmistakable physical status feedback even when looking away from the primary interface screen.

---

## 3. Removed Requirements History

* **US-003: Visitor temporary access**
  * *Statement:* As a visitor, I want the system registers me so that the system gives temporary access so that I can have an access to the lab.
  * *Reason for Removal:* Story wording was redundant and technically split. It has been completely replaced by the system-level automation defined in **US-013**, which correctly implements the secure data-management aspect of temporary profiles under administrator supervision.
* **US-009: Liveness detection check**
  * *Statement:* As a security manager, I want the system to perform a liveness detection check during the recognition process, so that unauthorized individuals cannot spoof the system using printed photos or digital screens.
  * *Reason for Removal:* Deemed out of scope for the core MVP delivery milestones due to processing overhead limitations on the target edge architecture. Suspended pending hardware acceleration optimization.
