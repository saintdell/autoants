# Social upload files

Made 2026-10-01 from the Logo Lab boards (rubber-hose mascot). Sizes come from each platform's own help pages; see `../mascot/social-specs-2026-10-01.json`.

| File | Where it goes |
|---|---|
| `profile-1080.png` | Profile picture on Instagram, YouTube and Facebook. All three crop it to a circle; the ant head stays inside. |
| `profile-400.png` | Profile picture on X, and the LinkedIn page logo (LinkedIn shows it square). |
| `x-header-1500x500.png` | X → Edit profile → header. Everything sits inside the middle 380 px, so X's top and bottom crop is safe. |
| `youtube-banner-2560x1440.png` | YouTube Studio → Customization → Branding → Banner image. Everything sits inside the 1546×423 area that shows on every device. |
| `facebook-cover-1702x630.png` | Facebook page → Edit cover photo. Exactly twice Facebook's 851×315, so it stays sharp on phones; the content is centered. |
| `linkedin-cover-1512x256.png` | LinkedIn page → Edit page → Cover image. The text starts 20% in, clear of the page logo that sits over the lower left. |

The mascot never goes on Google Business Profile, Apple Business or Yelp: their rules ban illustrated or edited images. Use the logo and real photos there.

## Post templates (`posts/`)

Seven starter posts, one per mascot pose, each in three formats in `posts/out/`:
- **feed** 1080×1350 for Instagram, Facebook and LinkedIn;
- **story** 1080×1920 for Instagram and Facebook stories (text stays clear of the top and bottom bars);
- **wide** 1920×1080 for X, LinkedIn and YouTube thumbnails.

To make a new post, add a row to `posts/posts.json` (slug, pose, eyebrow, line, sub) and run `python3 brand/social/posts/make_post.py <slug>`.
The poses are wave, phone, thumbs, clipboard, point, carry and hardhat.
Copy rules:
- one outcome per post;
- name the assistant's job, never lead with "AI";
- no numbers or results we can't show.
