### **Meeting Summary: FaceGuardV2 Project Sync**

#### **1. Project Status & MVP v0 Feedback**

* **General Status:** The customer confirmed that the current face recognition pipeline operates satisfactorily and is moving in the correct direction.

* **Edge Case Handling:** The customer noted that two people appeared in the frame during the demonstration and questioned how the system handles multi-face scenarios. Currently, this edge case is not yet handled by the development team.
* **Biometric Enrollment:** The customer validated the current approach of averaging face embeddings captured across 5 frames.

#### **2. MVP v1 Scope & Requirements**

* **Hardware Integration Timeline:** The team and the customer discussed the deployment schedule for physical hardware (Raspberry Pi/servo motor). While deploying hardware in Stage 2 is theoretically possible, the customer strongly recommended prioritizing it for MVP v1 to mitigate the risk of project failure.

* **Database & Persistence:** Integrating a functional database is confirmed as a strict requirement for MVP v1.
* **Administrative Operations:** The system must support core CRUD operations (Create, Read, Update, Delete) to handle database entities. The customer highlighted that admin access should be established securely over SSH.

* **User Registration Flow:** The customer rejected the idea of registering users retroactively via access logs. Instead, user registration must occur in real-time ("live format").

#### **3. User Interface & Administration Panel**

* **End-User Interface:** The primary graphical interface will remain an OpenCV live stream window displaying text overlays and relevant status indicators.

* **Admin Dashboard:** The system requires a lightweight web interface (a single-page application is sufficient).

* **Admin Features:** The dashboard must include basic navigation buttons to view logs, monitor system operations, and manage persistent or temporary user permissions. No advanced styling or complex UI components are required at this stage.
  