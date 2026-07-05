### Customer Review Summary

#### 1. Delivered Features & Demonstration
*   **Full CRUD Implementation:** Demonstrated the updated administrative panel. Administrators can now edit user names and dynamically modify access types. Switching a user to *Permanent* automatically nullifies the expiration field (`expires = null`), while selecting *Temporary* unlocks the expiration date picker.
*   **Active Liveness Detection:** Introduced an active biometric anti-spoofing mechanism based on eye blinking. The system utilizes a randomized timer (1–3 seconds) before prompting the user to blink, effectively preventing spoofing attempts using static photographs (even when shaking or moving the image).

#### 2. Limitations & Future Security Enhancements
*   **Video Bypass Vulnerability:** The current active blinking check can still be bypassed using a high-quality video recording of a registered user.
*   **Proposed Solutions:** The team suggested adding **Motion Control** (prompting the user to turn their head in a specific direction, guided by an LED indicator). Passive checks (texture or frequency analysis) were deemed ineffective due to the high display quality of modern smartphones.
*   **Client Alignment:** The client agreed that texture/frequency analysis requires heavy artifact-analysis models. They confirmed that **protection against photos is completely sufficient for the current scope**, while video anti-spoofing remains a major "bonus" asset for future development beyond the core project constraints.

#### 3. Technical Decisions & Resource Optimization
*   **Model Downsizing:** Confirmed the pipeline under the hood is migrating to `buffalo_sc`—a lightweight face recognition model highly optimized for CPU performance on edge devices.
*   **Threshold Calibration:** The team has begun actively tuning and selecting target confidence parameters and classification thresholds based on the downscaled model architecture.

#### 4. Hardware Deployment & Timeline Constraints
*   **Target Deployment:** Physical deployment and hardware integration tests on the Raspberry Pi have not yet been performed. The team scheduled live hardware testing for the upcoming week.
*   **Resource Alert:** The client recommended that the team source an independent SD card for their Raspberry Pi deployment, noting that laboratory cards are congested and have full storage.
*   **Project Defense:** The final project defense is tentatively expected around the 20th–21st of the month.