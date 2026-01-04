import os
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse

# Configuration
ORGANIZERS_DIR = "imgs/organizers"
SPEAKERS_DIR = "imgs/speakers"

# Headers to mimic a browser (prevents 403 Forbidden errors on some academic sites)
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
}

people = [
    # --- ORGANIZERS ---
    # Yining Hong (Stanford) - Known as Eveline Hong
    {"name": "Yining Hong", "role": "organizer", "url": "https://evelinehong.github.io/"}, 
    
    # Wenbo Hu (UCLA) - Based on your GitHub username
    {"name": "Wenbo Hu",    "role": "organizer", "url": "https://gordonhu608.github.io/"},
    
    # Jianing Yang (FIGURE AI / UMich) - Known as Jed Yang
    {"name": "Jianing Yang","role": "organizer", "url": "https://jedyang.com/"},
    
    # Shengyi Qian (Meta FAIR) - Known as Jason Qian
    {"name": "Shengyi Qian","role": "organizer", "url": "https://jasonqsy.github.io/"},
    
    # Valts Blukis (NVIDIA)
    {"name": "Valts Blukis","role": "organizer", "url": "https://www.cs.cornell.edu/~valts/"},
    
    # Yilun Du (Harvard)
    {"name": "Yilun Du",    "role": "organizer", "url": "https://yilundu.github.io/"},
    
    # Manling Li (Northwestern)
    {"name": "Manling Li",  "role": "organizer", "url": "https://limanling.github.io/"},
    
    # David Fouhey (NYU)
    {"name": "David Fouhey","role": "organizer", "url": "https://cs.nyu.edu/~fouhey/"},
    
    # Joyce Chai (UMich)
    {"name": "Joyce Chai",  "role": "organizer", "url": "https://web.eecs.umich.edu/~chaijy/"},
    
    # Jiajun Wu (Stanford)
    {"name": "Jiajun Wu",   "role": "organizer", "url": "https://jiajunwu.com/"},
    
    # Yejin Choi (Stanford/UW)
    {"name": "Yejin Choi",  "role": "organizer", "url": "https://homes.cs.washington.edu/~yejin/"},
    
    # --- SPEAKERS ---
    # Leonidas Guibas (Stanford)
    {"name": "Leonidas Guibas", "role": "speaker", "url": "https://profiles.stanford.edu/leonidas-guibas"}, 
    
    # Yue Wang (USC)
    {"name": "Yue Wang",        "role": "speaker", "url": "https://yuewang.xyz/"},
    
    # Ranjay Krishna (UW)
    {"name": "Ranjay Krishna",  "role": "speaker", "url": "https://ranjaykrishna.com/"},
    
    # Xiaolong Wang (UCSD)
    {"name": "Xiaolong Wang",   "role": "speaker", "url": "https://xiaolonw.github.io/"},
    
    # Angela Dai (TUM)
    {"name": "Angela Dai",      "role": "speaker", "url": "https://www.3dunderstanding.org/"},
    
    # Marc Pollefeys (ETH Zurich)
    {"name": "Marc Pollefeys",  "role": "speaker", "url": "https://people.inf.ethz.ch/pomarc/"},
]

def get_filename(name):
    """Converts 'Wenbo Hu' to 'wenbo_hu.png'"""
    return name.lower().replace(" ", "_") + ".png"

def find_best_image(soup, base_url, name):
    """
    Heuristic to find the best profile image:
    1. Check OpenGraph image (og:image) - usually the high-res social share image.
    2. Check img tags with 'profile', 'portrait', 'me', or the person's name in src/alt.
    """
    
    # 1. Try OpenGraph Image (High confidence)
    og_image = soup.find("meta", property="og:image")
    if og_image and og_image.get("content"):
        print(f"  Found OpenGraph image for {name}")
        return urljoin(base_url, og_image["content"])

    # 2. Search all images for keywords
    images = soup.find_all("img")
    keywords = ["profile", "portrait", "headshot", "avatar", "me", name.split()[0].lower()]
    
    for img in images:
        src = img.get("src", "")
        alt = img.get("alt", "")
        
        # Skip small icons/logos based on filename patterns
        if any(x in src.lower() for x in ["logo", "icon", "svg", "sprite"]):
            continue

        # Check if src or alt contains keywords
        if any(k in src.lower() for k in keywords) or any(k in alt.lower() for k in keywords):
            # Filter out tiny images if size attributes exist (very basic check)
            width = img.get("width")
            if width and width.isdigit() and int(width) < 50: 
                continue
                
            print(f"  Found potential profile image in <img> tag for {name}")
            return urljoin(base_url, src)

    return None

def download_and_save(image_url, folder, filename):
    try:
        if not image_url:
            return False
            
        r = requests.get(image_url, headers=HEADERS, stream=True, timeout=10)
        if r.status_code == 200:
            path = os.path.join(folder, filename)
            with open(path, 'wb') as f:
                for chunk in r.iter_content(1024):
                    f.write(chunk)
            print(f"  Saved to {path}")
            return True
        else:
            print(f"  Failed to download {image_url} (Status: {r.status_code})")
    except Exception as e:
        print(f"  Error downloading: {e}")
    return False

def main():
    # Ensure directories exist
    os.makedirs(ORGANIZERS_DIR, exist_ok=True)
    os.makedirs(SPEAKERS_DIR, exist_ok=True)

    for person in people:
        name = person["name"]
        role = person["role"]
        url = person["url"]
        
        if not url:
            print(f"Skipping {name}: No URL provided in script.")
            continue

        print(f"Processing {name} ({role})...")
        
        target_dir = ORGANIZERS_DIR if role == "organizer" else SPEAKERS_DIR
        filename = get_filename(name)
        
        try:
            # 1. Fetch Website
            response = requests.get(url, headers=HEADERS, timeout=10)
            if response.status_code != 200:
                print(f"  Could not access website: {url}")
                continue
                
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # 2. Find Image
            img_url = find_best_image(soup, url, name)
            
            # 3. Download
            if img_url:
                success = download_and_save(img_url, target_dir, filename)
                if not success:
                    print(f"  ! Could not download found image for {name}")
            else:
                print(f"  ! No suitable image found on page for {name}")

        except Exception as e:
            print(f"  Error processing {name}: {e}")

if __name__ == "__main__":
    main()