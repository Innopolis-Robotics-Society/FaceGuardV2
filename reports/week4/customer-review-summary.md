## Sprint Review

### 1. Sprint Goal
The primary goal for this sprint was to develop the core administrative dashboard and implement basic user access management functionalities for the FaceGuard contactless facial recognition access control system.

### 2. Completed Work
* **Admin Dashboard:** Designed and deployed the main administrative user interface.
* **User Registration Module:** Implemented the registration panel supporting two distinct access categories:
    * *Permanent Access:* Unlimited authorization period.
    * *Temporary Access:* Time-bound access featuring automated revocation upon expiration.
* **System Logs Visualization:** Integrated a system logging section to track and review real-time authentication and login histories.
* **User Deletion:** Implemented database-level deletion capabilities to clear user records directly from the interface.

### 3. Customer Feedback
* The demonstrated modules function smoothly and align with basic operational requirements.
* The client explicitly highlighted the lack of full CRUD (Create, Read, Update, Delete) capabilities, noting that the **Update** function was completely missing.
* The client recommended that the engineering team perform independent product research to uncover standard user-management practices and integrate them proactively.

### 4. User Acceptance Testing (UAT) Results
* **Status: Partial Pass**
* **Successful Scenarios:** Validation of permanent/temporary logic, expiration schedules, and profile removal.
* **Gaps Discovered:** Flaws in administrative user flows. There is currently no way to rectify typographical errors in a user's name or modify access settings (e.g., transitioning a profile from permanent to temporary) once created.

### 5. Quality Requirements
* **Security Specification:** The system must feature a **Liveness Detection** mechanism to mitigate security risks, preventing unauthorized entry using static printouts or digital photographs.
* **Current Status:** Unimplemented (Not ready during this sprint cycle).

### 6. Remaining Work (Carried Over & New Backlog)
1.  Develop and deploy the **Update** functionality (profile editing and access updates).
2.  Integrate, test, and tune the **Liveness Detection** module.
3.  Conduct product research on comprehensive user management operations to expand admin dashboard capabilities.