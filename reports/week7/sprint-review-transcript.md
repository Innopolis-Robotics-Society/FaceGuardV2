# Project Meeting Transcript

* **Speaker 2:** This is the first screen — the login page.
* **Speaker 2:** Now watch here. You can see the status LEDs: yellow means the liveness check is running, blue means access is granted, and red means the person was not recognized.
* **Speaker 2:** Right now it's showing red, because the face currently in front of the camera is not recognized.
* **Speaker 2:** Inference is currently running at around 20 to 24 FPS.
* **Customer (Speaker 1):** And this runs in the background, right — in the background?
* **Speaker 2:** Yes, exactly, in the background.
* **Customer (Speaker 1):** So it keeps working even while you're sitting on a different browser tab?
* **Speaker 2:** Yes, of course.
* **Speaker 2:** That's it overall — let us know if there's anything you'd like us to show or explain, or if you have any questions.
* **Customer (Speaker 1):** What about this person — they're not in the database?
* **Speaker 2:** Right, that's why it shows as denied. Regarding the logs — the system only writes a new entry when the state changes. So if the same person keeps standing in front of the camera and repeatedly gets denied, it doesn't keep writing "denied, denied, denied" — that's intentional, to avoid flooding the audit log.
* **Customer (Speaker 1):** Okay, I see it working. The confidence score is quite low, but let's deal with that later.
* **Speaker 2:** Right.
* **Customer (Speaker 1):** No other questions for now.
* **Customer (Speaker 1):** So, about the presentation — what else do we still need to do, or is this everything?
* **Speaker 2:** Picking the final threshold value still hasn't been done. I worked with the Raspberry Pi setup before and forgot about this task — but it's not complicated, the scripts for it are already written, we just need to run them and pick a value.
* **Speaker 2:** For the presentation, we still need to finish the documentation once everything is confirmed working, and we also need to record the live demo video.
* **Customer (Speaker 1):** Yes, that too.
* **Customer (Speaker 1):** Overall, I'm satisfied with the project as it stands.
