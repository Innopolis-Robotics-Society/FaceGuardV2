# Project Meeting Transcript

* **Customer (Speaker 1):** Why is the service offline?
* **Speaker 2:** There is a slight delay, but it is actually online.
* **Customer (Speaker 1):** Do I understand correctly that it also runs in the background while we are editing something on the passes page?
* **Speaker 2:** Naturally, everything is forwarded via WebSockets. Regarding logs: there aren't many of them here, plus every 30 days (can be configured to 15), old logs are automatically deleted. There are filters here, for example, and they work.
* **Customer (Speaker 1):** I want the pass to be issued based on a specific date, not by the number of days — entering the date in a simple format, and also choosing the expiration time (Expired) down to the hour and minute.

* **Speaker 2:** We will need to refine the Liveness system because it fails way too often at times. Currently, the user is visible, but they don't pass Liveness, or they pass it poorly. When we first did it, the problem was that people would hold a photo up to the camera, just shake it, and the system would let them through. Because of this, the algorithm was complicated: now a waiting timer of 1–2 seconds turns on, and then an interval of about 3 seconds is set, during which the user must specifically blink. In the end, we overcomplicated it, and the system works too slowly.
* **Customer (Speaker 1):** Is this currently running on a Raspberry Pi (Malinka)?
* **Speaker 2:** Yes, it's on a Raspberry Pi.
* **Customer (Speaker 1):** Do we have the smallest model running? Optimization can be achieved not only through the model but also through how the code is written. Extra copying operations and a complex back-and-forth between the backend and frontend can introduce latency. It's worth checking where packets can be trimmed, removing redundant code, or eliminating unnecessary copying of user embedding arrays, which can waste a lot of time and resources.
* **Speaker 3:** Is cleaning up the code and optimizing it the only refinement needed for submission?
* **Customer (Speaker 1):** Yes, technically everything works great right now. Also, the frame rate is currently sad (around 15 frames), try to squeeze the maximum out of the video stream — at least 24 or 30 frames per second. I don't really like how the frontend looks. It needs to be made simple, clear, and beautiful: adapt the interface, fix color consistency (right now the colors are hard to see, and the dark tables stand out too much). The backend must also be consistent.

* **Customer (Speaker 1):** The repository needs to be cleaned up: write a README, update descriptions, and add tags. The remaining documents for the OS can be left as they are if you want. The project should look solid in the organization.
* **Speaker 3:** What kind of documentation is needed exactly?
* **Customer (Speaker 1):** Update the book/guide where the main operating conditions and a section on how to launch everything should be detailed (a minimal set for the README). It would also be great to have an SSG (static site generator) with documentation on GitHub Pages.
* **Speaker 3:** It's already there for the project; it describes the architecture and principles of operation.
* **Customer (Speaker 1):** Great, then finish up the docs, clean up the repository, and tweak the frontend so that everything works even better.