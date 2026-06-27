import pandas as pd
import os

print("📊 Creating 10,000 unique URL dataset for you...\n")

os.makedirs('dataset', exist_ok=True)

# ============ 5000 LEGITIMATE URLs ============
legitimate = [
    'https://www.google.com', 'https://www.facebook.com', 'https://www.amazon.com',
    'https://www.microsoft.com', 'https://www.apple.com', 'https://www.netflix.com',
    'https://www.twitter.com', 'https://www.instagram.com', 'https://www.linkedin.com',
    'https://www.youtube.com', 'https://www.wikipedia.org', 'https://www.reddit.com',
    'https://www.github.com', 'https://www.stackoverflow.com', 'https://www.quora.com',
    'https://www.medium.com', 'https://www.airbnb.com', 'https://www.uber.com',
    'https://www.paypal.com', 'https://stripe.com', 'https://www.slack.com',
    'https://www.figma.com', 'https://www.notion.so', 'https://www.canva.com',
    'https://www.dropbox.com', 'https://www.onedrive.live.com', 'https://www.icloud.com',
    'https://www.gmail.com', 'https://www.outlook.com', 'https://www.spotify.com',
    'https://www.zoom.us', 'https://www.discord.com', 'https://www.telegram.org',
    'https://www.whatsapp.com', 'https://www.viber.com', 'https://www.signal.org',
    'https://www.skype.com', 'https://www.hangouts.google.com', 'https://www.teams.microsoft.com',
    'https://mail.google.com', 'https://drive.google.com', 'https://photos.google.com',
    'https://calendar.google.com', 'https://docs.google.com', 'https://sheets.google.com',
    'https://classroom.google.com', 'https://meet.google.com', 'https://keep.google.com',
    'https://maps.google.com', 'https://search.google.com', 'https://translate.google.com',
    'https://accounts.google.com', 'https://myaccount.google.com', 'https://console.cloud.google.com',
    'https://outlook.microsoft.com', 'https://office.microsoft.com', 'https://teams.microsoft.com',
    'https://onedrive.microsoft.com', 'https://xbox.microsoft.com', 'https://store.microsoft.com',
    'https://account.microsoft.com', 'https://support.microsoft.com', 'https://developer.microsoft.com',
    'https://azure.microsoft.com', 'https://powerbi.microsoft.com', 'https://sharepoint.microsoft.com',
    'https://aws.amazon.com', 'https://prime.amazon.com', 'https://music.amazon.com',
    'https://video.amazon.com', 'https://photos.amazon.com', 'https://appstore.amazon.com',
    'https://business.amazon.com', 'https://advertising.amazon.com', 'https://seller.amazon.com',
    'https://icloud.com', 'https://www.icloud.com', 'https://mail.icloud.com',
    'https://www.apple.com/icloud', 'https://appleid.apple.com', 'https://support.apple.com',
    'https://www.pinterest.com', 'https://www.snapchat.com', 'https://www.tiktok.com',
    'https://www.ebay.com', 'https://www.walmart.com', 'https://www.target.com',
    'https://www.bestbuy.com', 'https://www.costco.com', 'https://www.ikea.com',
    'https://www.h-m.com', 'https://www.forever21.com', 'https://www.zara.com',
    'https://www.booking.com', 'https://www.hotels.com', 'https://www.kayak.com',
    'https://www.skyscanner.com', 'https://www.tripadvisor.com', 'https://www.agoda.com',
    'https://www.bbc.com', 'https://www.cnn.com', 'https://www.reuters.com',
    'https://www.apnews.com', 'https://www.bbc.co.uk', 'https://www.theguardian.com',
    'https://www.nytimes.com', 'https://www.washingtonpost.com', 'https://www.wsj.com',
    'https://www.coursera.org', 'https://www.udemy.com', 'https://www.edx.org',
    'https://www.udacity.com', 'https://www.khanacademy.org', 'https://www.skillshare.com',
    'https://www.masterclass.com', 'https://www.pluralsight.com', 'https://www.linkedin-learning.com',
    'https://www.hulu.com', 'https://www.disneyplus.com', 'https://www.hbomax.com',
    'https://www.paramount.com', 'https://www.peacocktv.com', 'https://www.showtime.com',
    'https://www.crunchyroll.com', 'https://www.twitch.tv', 'https://www.dailymotion.com',
    'https://www.gitlab.com', 'https://bitbucket.org', 'https://www.digitalocean.com',
    'https://linode.com', 'https://www.heroku.com', 'https://www.vultr.com',
    'https://cloud.google.com', 'https://azure.microsoft.com', 'https://www.alibaba.cloud',
]

# ============ 5000 PHISHING URLs ============
phishing = [
    'http://amazon-verify.tk', 'http://amaz0n-account.ml', 'http://amazon-secure.ga',
    'http://amazon-confirm.cf', 'http://verify-amazon.xyz', 'http://amazon-login.tk',
    'http://amazon-payment.ml', 'http://secure-amazon.ga', 'http://amazon.verify.cf',
    'http://amazon-update.xyz', 'http://amazon-security.tk', 'http://amazon-access.ml',
    'http://amazon-auth.ga', 'http://amaz0n-login.cf', 'http://amazon-user.xyz',
    'http://google-verify.tk', 'http://g00gle-account.ml', 'http://google-secure.ga',
    'http://google-confirm.cf', 'http://verify-google.xyz', 'http://gmail-verify.tk',
    'http://google-login.ml', 'http://secure-google.ga', 'http://google.verify.cf',
    'http://google-update.xyz', 'http://google-security.tk', 'http://google-access.ml',
    'http://google-auth.ga', 'http://g0ogle-login.cf', 'http://google-user.xyz',
    'http://facebook-verify.tk', 'http://f4cebook-account.ml', 'http://facebook-secure.ga',
    'http://facebook-confirm.cf', 'http://verify-facebook.xyz', 'http://fb-verify.tk',
    'http://facebook-login.ml', 'http://secure-facebook.ga', 'http://facebook.verify.cf',
    'http://facebook-update.xyz', 'http://facebook-security.tk', 'http://facebook-access.ml',
    'http://facebook-auth.ga', 'http://f4ceb00k-login.cf', 'http://facebook-user.xyz',
    'http://paypal-verify.tk', 'http://p4yp4l-account.ml', 'http://paypal-secure.ga',
    'http://paypal-confirm.cf', 'http://verify-paypal.xyz', 'http://paypal-login.tk',
    'http://paypal-payment.ml', 'http://secure-paypal.ga', 'http://paypal.verify.cf',
    'http://paypal-update.xyz', 'http://paypal-security.tk', 'http://paypal-access.ml',
    'http://paypal-auth.ga', 'http://p4yp41-login.cf', 'http://paypal-user.xyz',
    'http://apple-verify.tk', 'http://4pple-account.ml', 'http://apple-secure.ga',
    'http://apple-confirm.cf', 'http://verify-apple.xyz', 'http://icloud-verify.tk',
    'http://apple-login.ml', 'http://secure-apple.ga', 'http://apple.verify.cf',
    'http://apple-update.xyz', 'http://apple-security.tk', 'http://apple-access.ml',
    'http://apple-auth.ga', 'http://4pp1e-login.cf', 'http://apple-user.xyz',
    'http://microsoft-verify.tk', 'http://m1cr0s0ft-account.ml', 'http://microsoft-secure.ga',
    'http://microsoft-confirm.cf', 'http://verify-microsoft.xyz', 'http://office365-verify.tk',
    'http://microsoft-login.ml', 'http://secure-microsoft.ga', 'http://microsoft.verify.cf',
    'http://microsoft-update.xyz', 'http://microsoft-security.tk', 'http://microsoft-access.ml',
    'http://microsoft-auth.ga', 'http://m1cr0s0ft-login.cf', 'http://microsoft-user.xyz',
    'http://instagram-verify.tk', 'http://1nstagram-account.ml', 'http://instagram-secure.ga',
    'http://instagram-confirm.cf', 'http://verify-instagram.xyz', 'http://ig-verify.tk',
    'http://instagram-login.ml', 'http://secure-instagram.ga', 'http://instagram.verify.cf',
    'http://instagram-update.xyz', 'http://instagram-security.tk', 'http://instagram-access.ml',
    'http://instagram-auth.ga', 'http://1nst4gr4m-login.cf', 'http://instagram-user.xyz',
    'http://linkedin-verify.tk', 'http://l1nkedin-account.ml', 'http://linkedin-secure.ga',
    'http://linkedin-confirm.cf', 'http://verify-linkedin.xyz', 'http://linkedin-login.tk',
    'http://linkedin-payment.ml', 'http://secure-linkedin.ga', 'http://linkedin.verify.cf',
    'http://linkedin-update.xyz', 'http://linkedin-security.tk', 'http://linkedin-access.ml',
    'http://linkedin-auth.ga', 'http://l1nk3d1n-login.cf', 'http://linkedin-user.xyz',
    'http://twitter-verify.tk', 'http://tw1tter-account.ml', 'http://twitter-secure.ga',
    'http://twitter-confirm.cf', 'http://verify-twitter.xyz', 'http://twitter-login.tk',
    'http://twitter-payment.ml', 'http://secure-twitter.ga', 'http://twitter.verify.cf',
    'http://twitter-update.xyz', 'http://twitter-security.tk', 'http://twitter-access.ml',
    'http://twitter-auth.ga', 'http://tw1tt3r-login.cf', 'http://twitter-user.xyz',
    'http://netflix-verify.tk', 'http://netf1ix-account.ml', 'http://netflix-secure.ga',
    'http://netflix-confirm.cf', 'http://verify-netflix.xyz', 'http://netflix-login.tk',
    'http://netflix-payment.ml', 'http://secure-netflix.ga', 'http://netflix.verify.cf',
    'http://netflix-update.xyz', 'http://netflix-security.tk', 'http://netflix-access.ml',
    'http://netflix-auth.ga', 'http://netfl1x-login.cf', 'http://netflix-user.xyz',
    'http://youtube-verify.tk', 'http://y0utube-account.ml', 'http://youtube-secure.ga',
    'http://youtube-confirm.cf', 'http://verify-youtube.xyz', 'http://youtube-login.tk',
    'http://youtube-payment.ml', 'http://secure-youtube.ga', 'http://youtube.verify.cf',
    'http://youtube-update.xyz', 'http://youtube-security.tk', 'http://youtube-access.ml',
    'http://youtube-auth.ga', 'http://y0utub3-login.cf', 'http://youtube-user.xyz',
    'http://spotify-verify.tk', 'http://sp0tify-account.ml', 'http://spotify-secure.ga',
    'http://spotify-confirm.cf', 'http://verify-spotify.xyz', 'http://spotify-login.tk',
    'http://spotify-payment.ml', 'http://secure-spotify.ga', 'http://spotify.verify.cf',
    'http://spotify-update.xyz', 'http://spotify-security.tk', 'http://spotify-access.ml',
    'http://spotify-auth.ga', 'http://sp0t1fy-login.cf', 'http://spotify-user.xyz',
    'http://discord-verify.tk', 'http://d1scord-account.ml', 'http://discord-secure.ga',
    'http://discord-confirm.cf', 'http://verify-discord.xyz', 'http://discord-login.tk',
    'http://discord-payment.ml', 'http://secure-discord.ga', 'http://discord.verify.cf',
    'http://discord-update.xyz', 'http://discord-security.tk', 'http://discord-access.ml',
    'http://discord-auth.ga', 'http://d1sc0rd-login.cf', 'http://discord-user.xyz',
]

# Generate variations
print("Generating 10,000 unique URLs...\n")

for i in range(1, 50):
    for url in legitimate[:100]:
        legitimate.append(url.replace('://', f'://s{i}.') if f's{i}.' not in url else url)
        legitimate.append(url.replace('www.', f'cdn{i}.') if 'cdn' not in url else url)
    
    for url in phishing[:100]:
        phishing.append(url.replace('.tk', f'{i}.tk') if f'{i}' not in url else url)
        phishing.append(url.replace('://', f'://v{i}.') if f'v{i}' not in url else url)

# Remove duplicates
legitimate = list(set(legitimate))[:5000]
phishing = list(set(phishing))[:5000]

# Create data
data = []
for url in legitimate:
    data.append({'url': url, 'label': 0})
for url in phishing:
    data.append({'url': url, 'label': 1})

df = pd.DataFrame(data)

# Save
csv_path = 'dataset/phishing_urls_clean.csv'
df.to_csv(csv_path, index=False, encoding='utf-8')

print(f"✅ SUCCESS! Dataset created!")
print(f"📊 Total URLs: {len(df):,}")
print(f"✓ Legitimate: {len(df[df['label']==0]):,}")
print(f"✓ Phishing: {len(df[df['label']==1]):,}")
print(f"💾 Saved to: {csv_path}\n")

# Show sample
print("Sample URLs:")
print(df.head(10))