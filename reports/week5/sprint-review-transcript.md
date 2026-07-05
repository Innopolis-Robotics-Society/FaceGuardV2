* **Speaker 1:** Can you see it?
* **Speaker 2:** Yes, I can see it.
* **Speaker 1:** Alright, let's start from the beginning. This is already the new version. Here we added liveness detection, and overall, we also added what you requested regarding CRUD operations for users—meaning the ability to change the user type and name. When we set it to permanent, the "expires" field becomes null, and when it's temporary, we can modify it. The logs are also visible on this page. And regarding liveness, it will be demonstrated right now. There. So, liveness works via blinking. That is, it's an active check, meaning it triggers a certain timer, waits for one to three seconds, and then triggers the exact moment when the person needs to blink. Now it will be shown how it works against photos and videos. It doesn't trigger against a photo, even if you shake the screen.
* **Speaker 2:** Uh-huh, cool, cool.
* **Speaker 1:** Right, but the check doesn't work against video, of course.
* **Speaker 2:** Ah, so it grants access via video?
* **Speaker 1:** Yes. As for how to counter video, we actually have an idea, but it's very difficult to implement in this project. In my opinion, we could add motion control. But then we would need to somehow notify the user that they need to turn in a certain direction. Maybe via an LED or something else.
* **Speaker 2:** Would it be possible to implement a passive liveness check instead?
* **Speaker 1:** Passive. Well, we had a passive check, meaning the one based on blinking. But a passive one won't work on video because... well, if we use texture analysis or frequency analysis, it still won't work because modern screens are very good nowadays.
* **Speaker 2:** Well yeah, it's quite complicated there, of course. You would need additional models to analyze artifacts. But the fact that you've already made a detection system against photos is already enough, honestly. Video is, let's say, a huge bonus that I'm not demanding, but if you have the energy and desire, that would be awesome. You could say it's beyond the scope of the project. Other than that, it's really great, well done.
* **Speaker 1:** Also, this week we have already started selecting the threshold parameters for the model. Under the hood, we plan to use `buffalo_sc`, a small model optimized for the CPU. So, we've put everything together there and will be evaluating the models.
* **Speaker 2:** Have you tested it on the hardware yet?
* **Speaker 1:** Not yet. We plan to come next week and deploy it on the hardware.
* **Speaker 2:** By the way, did they tell you the date of the project defense?
* **Speaker 3:** Around the 21st, I think? Sometime in the 20s.
* **Speaker 2:** Got it, alright. You actually need to hurry up with the hardware as well. And I advise you to find an SD card, because right now I haven't found an extra one in the lab yet. I will try to look for one specifically for you, because the one currently in the Raspberry Pi isn't enough for everyone—its memory is already full. Well, anyway, those are just details. But otherwise, well done, I see the project is working well.
* **Speaker 3:** Well, that's all, I think. Thank you for the feedback.