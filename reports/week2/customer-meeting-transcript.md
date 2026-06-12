**Participants:** **Dmitry**, **Customer**, **Egor**, **Nadezhda**

**Dmitry:** How should the temporary access process work?

**Customer:** During user registration, after capturing the face vector and entering details (name, surname, course, email, etc.), the administrator should be able to set access duration: either indefinite, until a specific date, or for a fixed time period.

**Dmitry:** Is it sufficient to detect photographs, or should the system also detect video spoofing?

**Customer:** At minimum, the system must reliably reject photographs. If you can also handle video attacks, that would be excellent.

**Egor:** Detecting photographs is relatively straightforward - we can use eye-based analysis.

**Customer:** Test whether the system still works when shown a video. Then we can evaluate additional measures.

**Egor:** We considered motion-based liveness checks, but that is quite complex. It would require adding dynamic prompts to instruct the user to turn their head or perform an action.

**Customer:** Another team had a similar idea - implementing a simple indicator. I can provide an LED: red for rejection, green for access granted, and yellow for calibration. This way, users receive immediate visual feedback.

**Dmitry:** The location has basement lighting from lamps. Should we add additional lighting for the camera?

**Customer:** That is an option. Feel free to add supplementary lighting if needed.

**Dmitry:** What happens if an unknown person tries to gain access multiple times in a row? Should we implement a blacklist?

**Customer:** Instead of a blacklist, we can flag repeated failed attempts in the logs - highlighting that the same individual has tried several times without success. This would appear suspicious and warrant attention.

**Dmitry:** Should the system process only one person at a time?

**Customer:** This issue has been raised before. The "crowd" problem is fundamentally difficult to solve. The simplest approach is to require one person to approach as close as possible and perform verification individually.

**Egor:** At what height should the camera be installed?

**Customer:** Approximately 1.60–1.70 meters.

**Egor:** In general terms, what should MVP v0 include? Here is my proposed list for the first version:
• Database table with ID, name, and face vector.
• Backend CRUD operations.
• Registration using five frames: capture five images, average them, and store the normalized averaged vector.
• Recognition: when approaching the door, capture images, extract the vector, normalize it, and compare against each vector in the database. Obtain a similarity score from 0 to 1 and decide whether to grant access. For now, there is no fixed threshold - it is essentially a random number.
• All of this runs on an emulator.

**Customer:** So this is the first version?

**Nadezhda:** Is this the first version? Then what is v0?

**Egor:** I thought this was v0.

**Nadezhda:** No, this is probably v1. As I understand it, v0 is the prototype - we implement the core concept, and some minor features should work. But I was not clear on which features from the assignment belong to v0.

**Customer:** In standard projects, v0 is usually a design mockup or simple clickable buttons to verify basic interaction.

**Dmitry:** So we have a window interface.

**Customer:** Let me reiterate the checkpoint work for MVP v0.

**Egor:** Currently, we are implementing face recognition via OpenCV. We detect a face, take a photo, then use the InsideFace library to extract a vector. We simulate database interaction by comparing the vector against stored vectors and output whether access is granted or denied.

**Customer:** Understood. Approved. Great.

**Egor:** What about user stories?

**Customer:** Do they need to be confirmed?

**Dmitry:** Let's confirm them. Have yours been confirmed?

**Customer:** Yes, they have. But let's focus on the ones where there is uncertainty, rather than those that are clearly approved.

**Dmitry:** Here are our stories.

**Customer:** All of them look fine. Let's approve all of them.
