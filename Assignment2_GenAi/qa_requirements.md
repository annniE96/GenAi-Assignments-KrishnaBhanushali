# Password Reset Requirement

- Registered customers can request a password reset by email.
- The reset link should expire after 15 minutes.
- The link must not be reusable after a successful reset.
- If the email address is not found, show a neutral message that does not reveal whether the account exists.
- Product note: confirm whether the link should remain valid until first login if the user takes longer than 15 minutes.
- If a reset attempt fails midway, the user can request a fresh link.
