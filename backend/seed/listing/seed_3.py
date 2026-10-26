"""Seed listings, part 3 of 3: 20 listings, one listing per model."""

from modules.phones.schemas import PhoneCreate
from seed.schemas import SeedListing

LISTINGS: list[SeedListing] = [
    SeedListing(
        user=5,
        phone=PhoneCreate(
            model_code="SM-F741U",
            model_name="Galaxy Z Flip6",
            os="android",
            camera_megapixels=50,
            battery_capacity=4000,
            display_size=6.7,
            description=(
                "Samsung Galaxy Z Flip6 was released in July 2024 as a clamshell foldable with the Snapdragon 8 Gen 3 "
                "for Galaxy chip, a 6.7-inch main display and a 3.4-inch cover screen. It has a 50 MP main camera, a "
                "12 MP ultra wide camera, 12 GB of RAM and IP48 water resistance."
            ),
            condition="average",
            condition_note=(
                "256 GB, Mint, unlocked. The crease is visible, the factory screen protector on the inner display "
                "has a small bubble near the hinge. Light scratches on the cover screen. The hinge holds every angle."
            ),
            price=330,
        ),
    ),
    SeedListing(
        user=6,
        phone=PhoneCreate(
            model_code="SM-F956U",
            model_name="Galaxy Z Fold6",
            os="android",
            camera_megapixels=50,
            battery_capacity=4400,
            display_size=7.6,
            description=(
                "Samsung Galaxy Z Fold6 was released in July 2024 as a book-style foldable with the Snapdragon 8 Gen 3 "
                "for Galaxy chip, a 7.6-inch main display and a 6.3-inch cover screen. It has a 50 MP main camera, a "
                "12 MP ultra wide, a 10 MP 3x telephoto, 12 GB of RAM and S Pen support."
            ),
            condition="for_repair",
            condition_note=(
                "512 GB, Silver Shadow. The inner display has a black vertical stripe along the fold and does not "
                "respond to touch on the left half. The cover screen, cameras and charging work. Sold for an inner "
                "screen replacement."
            ),
            price=370,
        ),
    ),
    SeedListing(
        user=0,
        phone=PhoneCreate(
            model_code="SM-F766U",
            model_name="Galaxy Z Flip7",
            os="android",
            camera_megapixels=50,
            battery_capacity=4300,
            display_size=6.9,
            description=(
                "Samsung Galaxy Z Flip7 was released in July 2025 as a clamshell foldable with the Exynos 2500 chip, "
                "a 6.9-inch main display and an edge-to-edge 4.1-inch FlexWindow cover screen. It has a 50 MP main "
                "camera, a 12 MP ultra wide camera, 12 GB of RAM and IP48 water resistance."
            ),
            condition="like_new",
            condition_note=(
                "256 GB, Blue Shadow, unlocked. Folded and unfolded with care, the crease is barely visible. No "
                "scratches on either screen. Samsung Care+ active. Box and the original case included."
            ),
            price=560,
        ),
    ),
    SeedListing(
        user=1,
        phone=PhoneCreate(
            model_code="SM-F966U",
            model_name="Galaxy Z Fold7",
            os="android",
            camera_megapixels=200,
            battery_capacity=4400,
            display_size=8.0,
            description=(
                "Samsung Galaxy Z Fold7 was released in July 2025 as a book-style foldable, 8.9 mm thick when folded "
                "and 215 g, with the Snapdragon 8 Elite for Galaxy chip, an 8-inch main display and a 6.5-inch cover "
                "screen. It has a 200 MP main camera, a 12 MP ultra wide and a 10 MP 3x telephoto. It has no S Pen "
                "support."
            ),
            condition="average",
            condition_note=(
                "512 GB, Jetblack, unlocked. Small dent on the hinge cover and light scratches on the cover screen. "
                "The inner display and its protector are intact, the crease is visible at an angle. All functions work."
            ),
            price=1020,
        ),
    ),
    SeedListing(
        user=2,
        phone=PhoneCreate(
            model_code="SM-A166U",
            model_name="Galaxy A16 5G",
            os="android",
            camera_megapixels=50,
            battery_capacity=5000,
            display_size=6.7,
            description=(
                "Samsung Galaxy A16 5G is a budget phone released in late 2024 with a 6.7-inch Super AMOLED display "
                "at 90 Hz and a MediaTek Dimensity 6300 chip in the US version. It has a 50 MP main camera, a 5 MP "
                "ultra wide and a 2 MP macro camera, a microSD slot and six years of OS updates."
            ),
            condition="average",
            condition_note=(
                "128 GB, Blue Black, unlocked. Scratches on the plastic back and a small crack in the corner of the "
                "screen protector, the display itself is not damaged. Battery lasts two days. Phone and charger."
            ),
            price=85,
        ),
    ),
    SeedListing(
        user=3,
        phone=PhoneCreate(
            model_code="SM-A366U",
            model_name="Galaxy A36 5G",
            os="android",
            camera_megapixels=50,
            battery_capacity=5000,
            display_size=6.7,
            description=(
                "Samsung Galaxy A36 5G was released in March 2025 with the Snapdragon 6 Gen 3 chip and a 6.7-inch "
                "Super AMOLED display at 120 Hz. It has a 50 MP main camera, an 8 MP ultra wide and a 5 MP macro "
                "camera, 45 W wired charging, IP67 water resistance and six years of OS updates."
            ),
            condition="like_new",
            condition_note=(
                "128 GB, Awesome Black, unlocked. Used for three months with a case, no scratches. Battery holds "
                "close to two days. Box and USB-C cable included."
            ),
            price=200,
        ),
    ),
    SeedListing(
        user=4,
        phone=PhoneCreate(
            model_code="GHL1X",
            model_name="Pixel 7a",
            os="android",
            camera_megapixels=64,
            battery_capacity=4385,
            display_size=6.1,
            description=(
                "Google Pixel 7a was released in May 2023 with the Google Tensor G2 chip, 8 GB of RAM and a 6.1-inch "
                "OLED display at 90 Hz. It has a 64 MP main camera and a 13 MP ultra wide camera, Face Unlock, a "
                "fingerprint sensor under the display and wireless charging."
            ),
            condition="for_repair",
            condition_note=(
                "128 GB, Charcoal. The battery is swollen and lifts the back cover, the phone shuts down below 30%. "
                "Screen and cameras work. Not recommended for daily use until the battery is replaced."
            ),
            price=55,
        ),
    ),
    SeedListing(
        user=5,
        phone=PhoneCreate(
            model_code="GKWS6",
            model_name="Pixel 8",
            os="android",
            camera_megapixels=50,
            battery_capacity=4575,
            display_size=6.2,
            description=(
                "Google Pixel 8 was released in October 2023 with the Google Tensor G3 chip, 8 GB of RAM and a "
                "6.2-inch Actua OLED display at 120 Hz. It has a 50 MP main camera and a 12 MP ultra wide camera "
                "with Magic Editor and Best Take, and seven years of OS and security updates."
            ),
            condition="average",
            condition_note=(
                "128 GB, Hazel, unlocked. Normal wear: light scratches on the screen and a scuff on the camera bar. "
                "Battery lasts a day with average use. All functions work. Phone only."
            ),
            price=190,
        ),
    ),
    SeedListing(
        user=6,
        phone=PhoneCreate(
            model_code="GC3VE",
            model_name="Pixel 8 Pro",
            os="android",
            camera_megapixels=50,
            battery_capacity=5050,
            display_size=6.7,
            description=(
                "Google Pixel 8 Pro was released in October 2023 with the Google Tensor G3 chip, 12 GB of RAM and a "
                "6.7-inch Super Actua LTPO OLED display at 1 to 120 Hz. It has a 50 MP main camera, a 48 MP ultra "
                "wide, a 48 MP 5x telephoto and a built-in temperature sensor."
            ),
            condition="like_new",
            condition_note=(
                "256 GB, Bay, unlocked. Kept in a case with a screen protector, no scratches or dents. Battery is "
                "in very good condition. Original box and cable included."
            ),
            price=320,
        ),
    ),
    SeedListing(
        user=0,
        phone=PhoneCreate(
            model_code="GKV4X",
            model_name="Pixel 8a",
            os="android",
            camera_megapixels=64,
            battery_capacity=4492,
            display_size=6.1,
            description=(
                "Google Pixel 8a was released in May 2024 with the Google Tensor G3 chip, 8 GB of RAM and a 6.1-inch "
                "Actua OLED display at 120 Hz. It has a 64 MP main camera and a 13 MP ultra wide camera, IP67 water "
                "resistance and seven years of OS and security updates."
            ),
            condition="average",
            condition_note=(
                "128 GB, Aloe, unlocked. Small scratches on the matte back and the aluminum frame. Screen protector "
                "on, the display is clean. Battery health 87%. Phone and USB-C cable."
            ),
            price=180,
        ),
    ),
    SeedListing(
        user=1,
        phone=PhoneCreate(
            model_code="GUR25",
            model_name="Pixel 9",
            os="android",
            camera_megapixels=50,
            battery_capacity=4700,
            display_size=6.3,
            description=(
                "Google Pixel 9 was released in August 2024 with the Google Tensor G4 chip, 12 GB of RAM and a "
                "6.3-inch Actua OLED display at 120 Hz. It has a 50 MP main camera, a 48 MP ultra wide camera, an "
                "ultrasonic fingerprint sensor and Gemini AI features."
            ),
            condition="like_new",
            condition_note=(
                "128 GB, Obsidian, unlocked. Battery health 94%. No scratches, used with a case and a screen "
                "protector. Box and cable included."
            ),
            price=330,
        ),
    ),
    SeedListing(
        user=2,
        phone=PhoneCreate(
            model_code="GZC4K",
            model_name="Pixel 9 Pro XL",
            os="android",
            camera_megapixels=50,
            battery_capacity=5060,
            display_size=6.8,
            description=(
                "Google Pixel 9 Pro XL was released in August 2024 with the Google Tensor G4 chip, 16 GB of RAM and a "
                "6.8-inch Super Actua LTPO OLED display at 1 to 120 Hz. It has a 50 MP main camera, a 48 MP ultra "
                "wide, a 48 MP 5x telephoto and a 42 MP front camera."
            ),
            condition="average",
            condition_note=(
                "256 GB, Hazel, unlocked. Scratches on the polished frame and one visible scratch on the screen in "
                "the lower part. Battery health 85%. All cameras and the fingerprint sensor work."
            ),
            price=390,
        ),
    ),
    SeedListing(
        user=3,
        phone=PhoneCreate(
            model_code="GTF7P",
            model_name="Pixel 9a",
            os="android",
            camera_megapixels=48,
            battery_capacity=5100,
            display_size=6.3,
            description=(
                "Google Pixel 9a was released in April 2025 with the Google Tensor G4 chip, 8 GB of RAM and a 6.3-inch "
                "Actua OLED display at up to 120 Hz. It has a 48 MP main camera and a 13 MP ultra wide camera in a "
                "flat camera design, IP68 water resistance and seven years of OS updates."
            ),
            condition="for_repair",
            condition_note=(
                "128 GB, Porcelain. The USB-C port is loose and charges only at a certain cable angle. The screen has "
                "a crack from the top right corner, touch works. Cameras work. Sold for port and screen repair."
            ),
            price=95,
        ),
    ),
    SeedListing(
        user=4,
        phone=PhoneCreate(
            model_code="GLBW0",
            model_name="Pixel 10",
            os="android",
            camera_megapixels=48,
            battery_capacity=4970,
            display_size=6.3,
            description=(
                "Google Pixel 10 was released in August 2025 with the Google Tensor G5 chip, 12 GB of RAM and a "
                "6.3-inch Actua OLED display at 120 Hz. It has a 48 MP main camera, a 13 MP ultra wide and a 10.8 MP "
                "5x telephoto, and Qi2 magnetic wireless charging (Pixelsnap)."
            ),
            condition="like_new",
            condition_note=(
                "128 GB, Indigo, unlocked. Battery health 97%. Under a year of use with a case, no scratches. Box, "
                "cable and the receipt included."
            ),
            price=450,
        ),
    ),
    SeedListing(
        user=5,
        phone=PhoneCreate(
            model_code="G4QUR",
            model_name="Pixel 10 Pro",
            os="android",
            camera_megapixels=50,
            battery_capacity=4870,
            display_size=6.3,
            description=(
                "Google Pixel 10 Pro was released in August 2025 with the Google Tensor G5 chip, 16 GB of RAM and a "
                "6.3-inch Super Actua LTPO OLED display at 1 to 120 Hz. It has a 50 MP main camera, a 48 MP ultra "
                "wide, a 48 MP 5x telephoto with Pro Res Zoom up to 100x and Qi2 magnetic charging."
            ),
            condition="average",
            condition_note=(
                "256 GB, Moonstone, unlocked. Light scratches on the back glass and the frame, the screen is clean "
                "under a protector. Battery health 92%. Everything works. Phone and cable."
            ),
            price=560,
        ),
    ),
    SeedListing(
        user=6,
        phone=PhoneCreate(
            model_code="GUL82",
            model_name="Pixel 10 Pro XL",
            os="android",
            camera_megapixels=50,
            battery_capacity=5200,
            display_size=6.8,
            description=(
                "Google Pixel 10 Pro XL was released in August 2025 with the Google Tensor G5 chip, 16 GB of RAM and "
                "a 6.8-inch Super Actua LTPO OLED display at 1 to 120 Hz. It has a 50 MP main camera, a 48 MP ultra "
                "wide, a 48 MP 5x telephoto, 45 W wired charging and 25 W Qi2.2 magnetic wireless charging."
            ),
            condition="like_new",
            condition_note=(
                "512 GB, Obsidian, unlocked. Battery health 96%. Preferred Care active. No marks on the screen or "
                "the frame. Full box included."
            ),
            price=720,
        ),
    ),
    SeedListing(
        user=0,
        phone=PhoneCreate(
            model_code="G4H7L",
            model_name="Pixel 10a",
            os="android",
            camera_megapixels=48,
            battery_capacity=5100,
            display_size=6.3,
            description=(
                "Google Pixel 10a was released in March 2026 with the Google Tensor G4 chip, a Titan M2 security chip "
                "and a 6.3-inch OLED display at 120 Hz. It has a 48 MP main camera and a 5100 mAh battery, and is the "
                "most affordable phone of the Pixel 10 lineup."
            ),
            condition="average",
            condition_note=(
                "128 GB, unlocked. Scratches on the back and a small dent on the bottom left corner from a drop. The "
                "screen has no damage. Battery lasts a full day. All functions work. Phone only."
            ),
            price=280,
        ),
    ),
    SeedListing(
        user=1,
        phone=PhoneCreate(
            model_code="GM45K",
            model_name="Pixel 11 Pro",
            os="android",
            camera_megapixels=50,
            battery_capacity=4850,
            display_size=6.3,
            description=(
                "Google Pixel 11 Pro was released in August 2026 with the 3 nm Google Tensor G6 chip and a 6.3-inch "
                "LTPO OLED display. It has a 50 MP main camera, a 48 MP ultra wide and a 48 MP periscope telephoto."
            ),
            condition="like_new",
            condition_note=(
                "256 GB, unlocked. Bought in September 2026, battery health 100%. Used with a case and a screen "
                "protector, looks new. Full box and the receipt included."
            ),
            price=870,
        ),
    ),
    SeedListing(
        user=2,
        phone=PhoneCreate(
            model_code="CPH2583",
            model_name="OnePlus 12",
            os="android",
            camera_megapixels=50,
            battery_capacity=5400,
            display_size=6.82,
            description=(
                "OnePlus 12 was released in the US in January 2024 with the Snapdragon 8 Gen 3 chip and a 6.82-inch "
                "QHD+ LTPO AMOLED display at 1 to 120 Hz. It has a 50 MP main camera, a 48 MP ultra wide and a 64 MP "
                "3x periscope telephoto with Hasselblad tuning, 80 W wired and 50 W wireless charging."
            ),
            condition="for_repair",
            condition_note=(
                "256 GB, Flowy Emerald. The display has a green tint and flickers at low brightness. The phone works "
                "normally: touch, cameras and charging are fine. No cracks on the glass. Sold for a display "
                "replacement."
            ),
            price=150,
        ),
    ),
    SeedListing(
        user=3,
        phone=PhoneCreate(
            model_code="CPH2655",
            model_name="OnePlus 13",
            os="android",
            camera_megapixels=50,
            battery_capacity=6000,
            display_size=6.82,
            description=(
                "OnePlus 13 was released in January 2025 with the Snapdragon 8 Elite chip and a 6.82-inch QHD+ LTPO "
                "AMOLED display at 1 to 120 Hz. It has three 50 MP rear cameras with a 3x periscope telephoto, a "
                "6000 mAh battery, 80 W wired and 50 W wireless charging, and IP68 and IP69 ratings."
            ),
            condition="average",
            condition_note=(
                "256 GB, Midnight Ocean, unlocked. Light scuffs on the vegan leather back and the frame corners. "
                "Screen has no scratches. Battery still lasts close to two days. Phone and the original charger."
            ),
            price=430,
        ),
    ),
]
