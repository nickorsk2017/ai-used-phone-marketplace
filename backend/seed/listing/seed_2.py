"""Seed listings, part 2 of 3: 20 listings, one listing per model."""

from modules.phones.schemas import PhoneCreate
from seed.schemas import SeedListing

LISTINGS: list[SeedListing] = [
    SeedListing(
        user=6,
        phone=PhoneCreate(
            model_code="A3257",
            model_name="iPhone 17 Pro Max",
            os="ios",
            camera_megapixels=48,
            battery_capacity=5088,
            display_size=6.9,
            description=(
                "iPhone 17 Pro Max was released in September 2025 with the A19 Pro chip, an aluminum unibody with "
                "vapor chamber cooling and a 6.9-inch ProMotion OLED display. It has three 48 MP rear cameras with a "
                "4x telephoto and is the first iPhone with a battery above 5000 mAh. The US model is eSIM only."
            ),
            condition="like_new",
            condition_note=(
                "512 GB, Deep Blue, unlocked. Battery health 98%. AppleCare+ active. No scratches, used with a "
                "MagSafe case and a screen protector. Full box included."
            ),
            price=1050,
        ),
    ),
    SeedListing(
        user=0,
        phone=PhoneCreate(
            model_code="A3260",
            model_name="iPhone Air",
            os="ios",
            camera_megapixels=48,
            battery_capacity=3149,
            display_size=6.5,
            description=(
                "iPhone Air was released in September 2025 as the thinnest iPhone, 5.6 mm, with a titanium frame, "
                "the A19 Pro chip and a 6.5-inch ProMotion OLED display. It has a single 48 MP Fusion camera, the "
                "Apple C1X modem and eSIM only, with no physical SIM tray."
            ),
            condition="average",
            condition_note=(
                "256 GB, Sky Blue, unlocked. Battery health 93%. Visible scratches on the back glass and a small "
                "scuff on the camera plateau. The frame is straight, not bent. Screen is clean. Phone only."
            ),
            price=610,
        ),
    ),
    SeedListing(
        user=1,
        phone=PhoneCreate(
            model_code="A3575",
            model_name="iPhone 17e",
            os="ios",
            camera_megapixels=48,
            battery_capacity=4005,
            display_size=6.1,
            description=(
                "iPhone 17e was released in March 2026 with the A19 chip, the Apple C1X modem and a 6.1-inch Super "
                "Retina XDR OLED display. It has a single 48 MP Fusion camera, Face ID, the Action button, MagSafe "
                "and Qi2 wireless charging, IP68 water resistance and a USB-C port."
            ),
            condition="like_new",
            condition_note=(
                "256 GB, Black, unlocked. Battery health 100%, 40 charge cycles. Received as a gift, used for a few "
                "weeks. No marks. Sealed accessories and box included."
            ),
            price=470,
        ),
    ),
    SeedListing(
        user=2,
        phone=PhoneCreate(
            model_code="A3472",
            model_name="iPhone 18 Pro",
            os="ios",
            camera_megapixels=48,
            battery_capacity=4288,
            display_size=6.3,
            description=(
                "iPhone 18 Pro was released in September 2026 with the 2 nm A20 Pro chip, 12 GB of RAM, the Apple C2 "
                "modem and a 6.3-inch ProMotion OLED display. It has a 48 MP main camera with variable aperture, "
                "48 MP ultra wide and telephoto cameras, and 40 W wired charging. The US model is eSIM only."
            ),
            condition="like_new",
            condition_note=(
                "256 GB, unlocked. Battery health 100%. Bought in September 2026, selling after switching to a "
                "company phone. Used with a case, no scratches. Full box with the receipt included."
            ),
            price=1020,
        ),
    ),
    SeedListing(
        user=3,
        phone=PhoneCreate(
            model_code="A3473",
            model_name="iPhone 18 Pro Max",
            os="ios",
            camera_megapixels=48,
            battery_capacity=5567,
            display_size=6.9,
            description=(
                "iPhone 18 Pro Max was released in September 2026 with the 2 nm A20 Pro chip, 12 GB of RAM, the Apple "
                "C2 modem and a 6.9-inch ProMotion OLED display. It has a 48 MP main camera with variable aperture, "
                "48 MP ultra wide and telephoto cameras, and up to 45 hours of video playback."
            ),
            condition="for_repair",
            condition_note=(
                "256 GB, unlocked. Dropped on concrete: the front glass is shattered and the display shows black "
                "spots in the lower half, touch works only at the top. Cameras and Face ID work. Battery health 100%. "
                "No AppleCare, sold for a display replacement."
            ),
            price=640,
        ),
    ),
    SeedListing(
        user=4,
        phone=PhoneCreate(
            model_code="SM-S911U",
            model_name="Galaxy S23",
            os="android",
            camera_megapixels=50,
            battery_capacity=3900,
            display_size=6.1,
            description=(
                "Samsung Galaxy S23 was released in February 2023 with the Snapdragon 8 Gen 2 for Galaxy chip and a "
                "6.1-inch Dynamic AMOLED 2X display at 120 Hz. It has a 50 MP main camera, a 12 MP ultra wide and a "
                "10 MP 3x telephoto, IP68 water resistance and wireless charging."
            ),
            condition="average",
            condition_note=(
                "128 GB, Phantom Black, unlocked. Light scratches on the screen and a scuff on the bottom frame. "
                "Battery holds a full day with normal use. Fingerprint sensor and all cameras work. Phone and "
                "USB-C cable."
            ),
            price=230,
        ),
    ),
    SeedListing(
        user=5,
        phone=PhoneCreate(
            model_code="SM-S918U",
            model_name="Galaxy S23 Ultra",
            os="android",
            camera_megapixels=200,
            battery_capacity=5000,
            display_size=6.8,
            description=(
                "Samsung Galaxy S23 Ultra was released in February 2023 with the Snapdragon 8 Gen 2 for Galaxy chip "
                "and a 6.8-inch QHD+ Dynamic AMOLED 2X display at 120 Hz. It has a 200 MP main camera, 3x and 10x "
                "telephoto cameras with 100x Space Zoom and a built-in S Pen."
            ),
            condition="for_repair",
            condition_note=(
                "256 GB, Green. The S Pen is lost and the display has a pink line and burn-in from the keyboard. "
                "Touch, cameras and charging work. Back glass has no cracks. Sold for a screen replacement."
            ),
            price=210,
        ),
    ),
    SeedListing(
        user=6,
        phone=PhoneCreate(
            model_code="SM-S711U",
            model_name="Galaxy S23 FE",
            os="android",
            camera_megapixels=50,
            battery_capacity=4500,
            display_size=6.4,
            description=(
                "Samsung Galaxy S23 FE was released in October 2023 with the Snapdragon 8 Gen 1 chip in the US and a "
                "6.4-inch Dynamic AMOLED 2X display at 120 Hz. It has a 50 MP main camera, a 12 MP ultra wide and an "
                "8 MP 3x telephoto, IP68 water resistance and wireless charging."
            ),
            condition="average",
            condition_note=(
                "128 GB, Mint, unlocked. Small chip on the top left corner of the frame and light scratches on the "
                "back. Screen protector installed, the display under it is clean. All functions work."
            ),
            price=170,
        ),
    ),
    SeedListing(
        user=0,
        phone=PhoneCreate(
            model_code="SM-S921U",
            model_name="Galaxy S24",
            os="android",
            camera_megapixels=50,
            battery_capacity=4000,
            display_size=6.2,
            description=(
                "Samsung Galaxy S24 was released in January 2024 with the Snapdragon 8 Gen 3 for Galaxy chip in the "
                "US and a 6.2-inch Dynamic AMOLED 2X display at 1 to 120 Hz. It has a 50 MP main camera, a 12 MP "
                "ultra wide and a 10 MP 3x telephoto, Galaxy AI features and seven years of OS updates."
            ),
            condition="like_new",
            condition_note=(
                "256 GB, Cobalt Violet, unlocked. Used with a case and a screen protector, no scratches or dents. "
                "Battery lasts a full day. Original box and cable included."
            ),
            price=330,
        ),
    ),
    SeedListing(
        user=1,
        phone=PhoneCreate(
            model_code="SM-S926U",
            model_name="Galaxy S24+",
            os="android",
            camera_megapixels=50,
            battery_capacity=4900,
            display_size=6.7,
            description=(
                "Samsung Galaxy S24+ was released in January 2024 with the Snapdragon 8 Gen 3 for Galaxy chip in the "
                "US, 12 GB of RAM and a 6.7-inch QHD+ Dynamic AMOLED 2X display at 1 to 120 Hz. It has a 50 MP main "
                "camera, a 12 MP ultra wide, a 10 MP 3x telephoto and 45 W wired charging."
            ),
            condition="average",
            condition_note=(
                "256 GB, Onyx Black, unlocked. Noticeable scratches on the screen, not visible when the display is "
                "on, and wear on the frame corners. Battery is good. All cameras and the fingerprint sensor work."
            ),
            price=320,
        ),
    ),
    SeedListing(
        user=2,
        phone=PhoneCreate(
            model_code="SM-S928U",
            model_name="Galaxy S24 Ultra",
            os="android",
            camera_megapixels=200,
            battery_capacity=5000,
            display_size=6.8,
            description=(
                "Samsung Galaxy S24 Ultra was released in January 2024 with the Snapdragon 8 Gen 3 for Galaxy chip, a "
                "titanium frame and a flat 6.8-inch QHD+ Dynamic AMOLED 2X display with an anti-reflective Gorilla "
                "Armor cover. It has a 200 MP main camera, 3x and 5x telephoto cameras and a built-in S Pen."
            ),
            condition="like_new",
            condition_note=(
                "512 GB, Titanium Gray, unlocked. S Pen included and works. No scratches on the screen or the "
                "titanium frame, always in a case. Box and cable included."
            ),
            price=560,
        ),
    ),
    SeedListing(
        user=3,
        phone=PhoneCreate(
            model_code="SM-S721U",
            model_name="Galaxy S24 FE",
            os="android",
            camera_megapixels=50,
            battery_capacity=4700,
            display_size=6.7,
            description=(
                "Samsung Galaxy S24 FE was released in October 2024 with the Exynos 2400e chip and a 6.7-inch Dynamic "
                "AMOLED 2X display at 120 Hz. It has a 50 MP main camera, a 12 MP ultra wide and an 8 MP 3x "
                "telephoto, IP68 water resistance and Galaxy AI features."
            ),
            condition="for_repair",
            condition_note=(
                "128 GB, Blue. The phone restarts on its own every few minutes and gets hot near the cameras. The "
                "screen and the body have no cracks. Reset to factory settings, Google account removed. Sold for "
                "repair or parts."
            ),
            price=110,
        ),
    ),
    SeedListing(
        user=4,
        phone=PhoneCreate(
            model_code="SM-S931U",
            model_name="Galaxy S25",
            os="android",
            camera_megapixels=50,
            battery_capacity=4000,
            display_size=6.2,
            description=(
                "Samsung Galaxy S25 was released in February 2025 with the Snapdragon 8 Elite for Galaxy chip, 12 GB "
                "of RAM and a 6.2-inch Dynamic AMOLED 2X display at 1 to 120 Hz. It has a 50 MP main camera, a 12 MP "
                "ultra wide and a 10 MP 3x telephoto, and ships with Android 15 and One UI 7."
            ),
            condition="average",
            condition_note=(
                "128 GB, Icy Blue, unlocked. One deep scratch on the back glass and small scuffs on the frame. The "
                "screen is clean. All functions work. Phone and USB-C cable."
            ),
            price=380,
        ),
    ),
    SeedListing(
        user=5,
        phone=PhoneCreate(
            model_code="SM-S936U",
            model_name="Galaxy S25+",
            os="android",
            camera_megapixels=50,
            battery_capacity=4900,
            display_size=6.7,
            description=(
                "Samsung Galaxy S25+ was released in February 2025 with the Snapdragon 8 Elite for Galaxy chip, 12 GB "
                "of RAM and a 6.7-inch QHD+ Dynamic AMOLED 2X display at 1 to 120 Hz. It has a 50 MP main camera, a "
                "12 MP ultra wide, a 10 MP 3x telephoto and 45 W wired charging."
            ),
            condition="like_new",
            condition_note=(
                "256 GB, Navy, unlocked. Samsung Care+ until March 2027. No scratches, screen protector and case "
                "since purchase. Original box included."
            ),
            price=520,
        ),
    ),
    SeedListing(
        user=6,
        phone=PhoneCreate(
            model_code="SM-S938U",
            model_name="Galaxy S25 Ultra",
            os="android",
            camera_megapixels=200,
            battery_capacity=5000,
            display_size=6.9,
            description=(
                "Samsung Galaxy S25 Ultra was released in February 2025 with the Snapdragon 8 Elite for Galaxy chip, "
                "a titanium frame and a 6.9-inch QHD+ Dynamic AMOLED 2X display with Gorilla Armor 2. It has a 200 MP "
                "main camera, a 50 MP ultra wide, 3x and 5x telephoto cameras and a built-in S Pen without Bluetooth."
            ),
            condition="average",
            condition_note=(
                "256 GB, Titanium Silverblue, unlocked. Light scratches on the titanium frame and the camera rings. "
                "Screen has a protector and no scratches under it. S Pen included. All functions work."
            ),
            price=640,
        ),
    ),
    SeedListing(
        user=0,
        phone=PhoneCreate(
            model_code="SM-S937U",
            model_name="Galaxy S25 Edge",
            os="android",
            camera_megapixels=200,
            battery_capacity=3900,
            display_size=6.7,
            description=(
                "Samsung Galaxy S25 Edge was released in May 2025 as a 5.8 mm thin phone with a titanium frame, the "
                "Snapdragon 8 Elite for Galaxy chip and a 6.7-inch QHD+ Dynamic AMOLED 2X display. It has a 200 MP "
                "main camera and a 12 MP ultra wide camera, with no telephoto."
            ),
            condition="like_new",
            condition_note=(
                "256 GB, Titanium Jetblack, unlocked. Looks new, no marks on the screen or the frame. Battery lasts a "
                "full day with moderate use. Box, cable and a clear case included."
            ),
            price=470,
        ),
    ),
    SeedListing(
        user=1,
        phone=PhoneCreate(
            model_code="SM-S731U",
            model_name="Galaxy S25 FE",
            os="android",
            camera_megapixels=50,
            battery_capacity=4900,
            display_size=6.7,
            description=(
                "Samsung Galaxy S25 FE was released in September 2025 with the Exynos 2400 chip, 8 GB of RAM and a "
                "6.7-inch Dynamic AMOLED 2X display at 120 Hz. It has a 50 MP main camera, a 12 MP ultra wide, an "
                "8 MP 3x telephoto, 45 W wired charging and IP68 water resistance."
            ),
            condition="average",
            condition_note=(
                "128 GB, Navy, unlocked. Small dent on the right side near the power button and light scratches on "
                "the screen. No cracks. All buttons, cameras and the fingerprint sensor work."
            ),
            price=300,
        ),
    ),
    SeedListing(
        user=2,
        phone=PhoneCreate(
            model_code="SM-S942U",
            model_name="Galaxy S26",
            os="android",
            camera_megapixels=50,
            battery_capacity=4300,
            display_size=6.3,
            description=(
                "Samsung Galaxy S26 was released in February 2026 with the Snapdragon 8 Elite Gen 5 for Galaxy chip "
                "in the US, 12 GB of RAM and a 6.3-inch Dynamic AMOLED 2X display. It has a 50 MP main camera, a "
                "12 MP ultra wide and a 10 MP 3x telephoto, and ships with Android 16 and One UI 8.5."
            ),
            condition="like_new",
            condition_note=(
                "256 GB, Cobalt Violet, unlocked. Bought in April 2026. No scratches, used with a case and a screen "
                "protector. Battery health is excellent. Full box included."
            ),
            price=590,
        ),
    ),
    SeedListing(
        user=3,
        phone=PhoneCreate(
            model_code="SM-S947U",
            model_name="Galaxy S26+",
            os="android",
            camera_megapixels=50,
            battery_capacity=4900,
            display_size=6.7,
            description=(
                "Samsung Galaxy S26+ was released in February 2026 with the Snapdragon 8 Elite Gen 5 for Galaxy chip "
                "in the US, 12 GB of RAM and a 6.7-inch QHD+ Dynamic LTPO AMOLED 2X display. It has a 50 MP main "
                "camera, a 12 MP ultra wide, a 10 MP 3x telephoto, 45 W wired and 20 W Qi2.2 wireless charging."
            ),
            condition="for_repair",
            condition_note=(
                "256 GB, unlocked. The main and telephoto cameras show a black screen in the camera app, the ultra "
                "wide and the front camera work. Display, charging and calls work. A thin crack on the camera glass. "
                "Sold for camera module repair."
            ),
            price=330,
        ),
    ),
    SeedListing(
        user=4,
        phone=PhoneCreate(
            model_code="SM-S948U",
            model_name="Galaxy S26 Ultra",
            os="android",
            camera_megapixels=200,
            battery_capacity=5000,
            display_size=6.9,
            description=(
                "Samsung Galaxy S26 Ultra was released in February 2026 with the Snapdragon 8 Elite Gen 5 for Galaxy "
                "chip, 12 GB of RAM and a 6.9-inch QHD+ Dynamic AMOLED 2X display with a built-in privacy mode. It has "
                "a 200 MP main camera, a 50 MP ultra wide, 50 MP and 10 MP telephoto cameras and a built-in S Pen."
            ),
            condition="average",
            condition_note=(
                "512 GB, Black, unlocked. Scratches on the frame from use without a case and a small scuff on the "
                "screen edge. S Pen included and works. Battery and all cameras work well."
            ),
            price=860,
        ),
    ),
]
