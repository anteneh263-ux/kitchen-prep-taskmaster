# Final Submission Checklist

This checklist maps the current project to the binding contest requirements.
Do not submit until every unchecked item is complete.

## Eligibility — entrant must confirm personally

- [ ] Entrant is above the age of majority in Norway.
- [ ] Entrant is not subject to the listed sanctions or exclusion territories.
- [ ] Entrant is not an employee, contractor, household member or other
      ineligible party described in the Official Rules.
- [ ] Participation does not violate an employer policy or create a real or
      apparent conflict of interest.
- [ ] Every team member, if any, is listed on Devpost and eligible.

## Project requirements

- [x] Newly created during the submission period; first commit 2026-08-11.
- [x] Category: The Taskmaster.
- [x] Autonomous multi-step workflow rather than a chat loop.
- [x] Gemini 3.5 Flash used through the Google Gen AI SDK.
- [x] Google agent framework requirement met by Google Gen AI SDK.
- [x] Google Cloud infrastructure: Cloud Run, Firestore and Scheduler.
- [x] Built and deployed on Google Cloud.
- [x] Application supports English; Norwegian is optional.
- [x] Public code repository with reproducible spin-up instructions.
- [x] Architecture diagram and detailed architecture document.
- [x] Public, free, credential-free read-only judge URL.
- [x] Third-party components, synthetic data and AI coding assistance disclosed.
- [x] No confidential data or committed secrets.

## Production verification

- [x] Private worker revision `kitchen-prep-taskmaster-web-00006-jgp` serves 100%.
- [x] Public viewer revision `kitchen-prep-viewer-00007-zld` serves 100%.
- [x] Scheduler `kitchen-prep-daily` is enabled for 07:00 Europe/Oslo.
- [x] Production run reports `forecast_source: gemini` and `gemini_ok`.
- [x] Production run reports `briefing_source: gemini`.
- [x] Forced replay preserves identical FEFO consumption and remaining stock.
- [x] Public viewer mutation route and API docs return 404.
- [x] Offline suite: 124 passed; live-key integration path separately verified in
      production.

## Devpost fields

- [ ] Project name and tagline entered.
- [ ] The Taskmaster selected as the single category.
- [ ] English project description entered from `docs/devpost_submission.md`.
- [ ] Hosted viewer URL entered.
- [ ] Public GitHub URL entered.
- [ ] Architecture diagram uploaded.
- [ ] Judge testing instructions entered.
- [ ] Public YouTube or Vimeo demo URL entered.
- [ ] Official Rules acceptance box checked only after final review.

## Mandatory video

- [ ] Final duration is under 4:00.
- [ ] Video is public, not private or unlisted.
- [ ] English narration or complete English subtitles.
- [ ] Problem and value proposition shown in the first 30 seconds.
- [ ] Live, unedited agent execution shown.
- [ ] Cloud Run service/revision and 100% traffic shown.
- [ ] Cloud Scheduler schedule and enabled state shown.
- [ ] Terminal response visibly shows Gemini source and `gemini_ok`.
- [ ] Refreshed dashboard visibly proves operational output.
- [ ] No API key, identity token, private data or unrelated tab is visible.
- [ ] Video statements match the repository and deployed behavior exactly.

## Final deadline controls

- [ ] Submission preview checked on desktop and mobile.
- [ ] Every link opened in a signed-out/incognito window.
- [ ] Submission moved from Draft to Submitted before
      **2026-09-01 02:00 Europe/Oslo**.
- [ ] Confirmation page/email saved.
- [ ] Project remains available without charge or restriction through the end of
      judging on 2026-10-01 PT.
- [ ] Email monitored after judging; potential winners may have only two days to
      respond to a verification request.

## Optional bonus

- [ ] Public build article/video explicitly says it was created for entry into
      the All Things Agentic Hackathon.
- [ ] Social post includes `#AllThingsAgenticHackathon`.
- [ ] Any additional Google AI model is genuinely integrated and demonstrated;
      do not add a decorative model call solely for bonus points.
