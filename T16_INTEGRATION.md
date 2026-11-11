
# T16 — Private Edit Links and Spam Protection

## Implemented Features

- Unique private UUID edit tokens for posts.
- Editing posts without creating an account.
- Moderator review required after editing a post.
- Google reCAPTCHA v2 server-side verification.
- Five successful post submissions per IP per hour.
- Database locking to prevent concurrent limit bypasses.
- Automated tests for editing and spam protection.

## Environment Configuration

The following environment variables are required:

- SECRET_KEY
- RECAPTCHA_SITE_KEY
- RECAPTCHA_SECRET_KEY

Keep actual secret values in a private .env file.

## Integration With Public Post Submission

Neil's public submission form must:

1. Validate the submitted post information.
2. Display Google reCAPTCHA v2 using RECAPTCHA_SITE_KEY.
3. Call submit_post() from board/post_submission.py.
4. Ensure the save callback creates posts with status="pending".
5. Handle CaptchaVerificationFailed and PostRateLimitExceeded.
6. Give the resident their private edit link securely.

Private edit links use the route:

/posts/edit/<uuid:token>/

Do not display private edit links on public post pages.

## Deployment Considerations

- Configure real Google reCAPTCHA keys for the deployed domain.
- Verify visitor IP identification behind the AWS proxy.
- Configure the SECRET_KEY environment variable.
- Use HTTPS for private edit links.
- Ensure the old hard-coded Django secret key is not reused.

## Testing

- All 31 automated tests passed.
- MySQL concurrent submission test passed:
  5 accepted, 3 blocked, 0 unexpected errors.

## Outstanding Integration

- Connect the public post submission form.
- Display and verify reCAPTCHA in the real submission workflow.
- Deliver private edit links to residents.
- Confirm AWS proxy and production configuration.
