"""Seed listings, part 4 of 5: 14 listings of Xiaomi, POCO, Huawei and Honor, one listing per model."""

from modules.phones.schemas import PhoneCreate
from seed.schemas import SeedListing

LISTINGS: list[SeedListing] = [
    SeedListing(
        user=1,
        phone=PhoneCreate(
            model_code="25010PN30G",
            model_name="Xiaomi 15 Ultra",
            os="android",
            camera_megapixels=50,
            battery_capacity=5410,
            display_size=6.73,
            description=(
                "Xiaomi 15 Ultra was released globally in March 2025 with the Snapdragon 8 Elite chip and a 6.73-inch "
                "QHD+ LTPO AMOLED display. It has a Leica quad camera with a 50 MP 1-inch main sensor, a 50 MP 3x "
                "telephoto, a 200 MP 4.3x periscope and a 50 MP ultra wide, 90 W wired and 80 W wireless charging, and "
                "IP68."
            ),
            condition="average",
            condition_note=(
                "512 GB, Silver Chrome, global version. Light scratches on the vegan leather back and one small dent "
                "on the bottom frame. Screen is clean with a protector applied since day one. All four cameras work. "
                "Battery health 89%. Phone and the original 90 W charger."
            ),
            price=520,
        ),
    ),
    SeedListing(
        user=2,
        phone=PhoneCreate(
            model_code="25128PNA1G",
            model_name="Xiaomi 17 Ultra",
            os="android",
            camera_megapixels=50,
            battery_capacity=6000,
            display_size=6.9,
            description=(
                "Xiaomi 17 Ultra was released globally in March 2026 with the Snapdragon 8 Elite Gen 5 chip and a "
                "6.9-inch LTPO AMOLED display. It has a Leica camera with a 50 MP 1-inch main sensor, a 200 MP "
                "periscope telephoto with 3.2x to 4.3x optical zoom and a 50 MP ultra wide, a 6000 mAh battery and "
                "IP68 and IP69 ratings."
            ),
            condition="like_new",
            condition_note=(
                "512 GB, Black, global version. Bought in March 2026, used in a case with a screen protector. No "
                "scratches or marks. Battery health 100%. Full box with the charger, cable and the unused case."
            ),
            price=980,
        ),
    ),
    SeedListing(
        user=3,
        phone=PhoneCreate(
            model_code="2506BPN68G",
            model_name="Xiaomi 15T Pro",
            os="android",
            camera_megapixels=50,
            battery_capacity=5500,
            display_size=6.83,
            description=(
                "Xiaomi 15T Pro was released in September 2025 with the MediaTek Dimensity 9400+ chip and a 6.83-inch "
                "144 Hz AMOLED display. It has a Leica triple camera with a 50 MP main, a 50 MP 5x periscope telephoto "
                "and a 12 MP ultra wide, 90 W wired and 50 W wireless charging, and IP68."
            ),
            condition="like_new",
            condition_note=(
                "256 GB, Mocha Gold, unlocked. Used for four months in a case. No scratches on the screen or the "
                "frame. Battery health 98%. Box, cable and the 90 W charger included."
            ),
            price=430,
        ),
    ),
    SeedListing(
        user=4,
        phone=PhoneCreate(
            model_code="25069PTEBG",
            model_name="Xiaomi 15T",
            os="android",
            camera_megapixels=50,
            battery_capacity=5500,
            display_size=6.83,
            description=(
                "Xiaomi 15T was released in September 2025 with the MediaTek Dimensity 8400-Ultra chip and a 6.83-inch "
                "120 Hz AMOLED display. It has a Leica triple camera with a 50 MP main, a 50 MP 2x telephoto and a 12 "
                "MP ultra wide, a 5500 mAh battery, 67 W charging and IP68."
            ),
            condition="average",
            condition_note=(
                "256 GB, Gray. Visible scratches on the screen in sunlight and scuffs on the back glass corners. "
                "Cameras, speakers and charging work. Battery holds a full day. Phone only, no charger."
            ),
            price=280,
        ),
    ),
    SeedListing(
        user=5,
        phone=PhoneCreate(
            model_code="24117RK2CG",
            model_name="POCO F7 Pro",
            os="android",
            camera_megapixels=50,
            battery_capacity=6000,
            display_size=6.67,
            description=(
                "POCO F7 Pro was released in March 2025 with the Snapdragon 8 Gen 3 chip and a 6.67-inch QHD+ 120 Hz "
                "AMOLED display. It has a 50 MP main camera with OIS and an 8 MP ultra wide, a 6000 mAh battery, 90 W "
                "charging and IP68."
            ),
            condition="for_repair",
            condition_note=(
                "512 GB, Blue. The back glass is shattered and the phone restarts when the battery is below 20%. The "
                "screen, touch and cameras work. Sold for a back glass and battery replacement."
            ),
            price=140,
        ),
    ),
    SeedListing(
        user=6,
        phone=PhoneCreate(
            model_code="25053PC47G",
            model_name="POCO F7",
            os="android",
            camera_megapixels=50,
            battery_capacity=6500,
            display_size=6.83,
            description=(
                "POCO F7 was released in June 2025 with the Snapdragon 8s Gen 4 chip and a 6.83-inch 120 Hz AMOLED "
                "display. It has a 50 MP main camera with OIS and an 8 MP ultra wide, a 6500 mAh battery, 90 W "
                "charging and IP68."
            ),
            condition="like_new",
            condition_note=(
                "256 GB, Cyber Silver Edition. Used for two months in a case with a screen protector. No marks. "
                "Battery health 99%. Box and the original charger included."
            ),
            price=290,
        ),
    ),
    SeedListing(
        user=0,
        phone=PhoneCreate(
            model_code="LMU-LX9",
            model_name="Huawei Pura 80 Ultra",
            os="android",
            camera_megapixels=50,
            battery_capacity=5170,
            display_size=6.8,
            description=(
                "Huawei Pura 80 Ultra was released in June 2025 with the Kirin 9020 chip and a 6.8-inch LTPO OLED "
                "display. It has a 50 MP 1-inch main camera with a variable aperture, a switchable periscope telephoto "
                "with 50 MP 3.7x and 12.5 MP 9.4x lenses and a 40 MP ultra wide, 100 W wired and 80 W wireless "
                "charging, and IP68 and IP69. It runs EMUI without Google services."
            ),
            condition="like_new",
            condition_note=(
                "512 GB, Prestige Gold, international version. Used for one month, then kept in the box. No scratches. "
                "Battery health 100%. Full box with the 100 W charger and the case."
            ),
            price=890,
        ),
    ),
    SeedListing(
        user=1,
        phone=PhoneCreate(
            model_code="LMR-LX9",
            model_name="Huawei Pura 80 Pro",
            os="android",
            camera_megapixels=50,
            battery_capacity=5170,
            display_size=6.8,
            description=(
                "Huawei Pura 80 Pro was released in June 2025 with a 6.8-inch LTPO OLED display. It has a 50 MP 1-inch "
                "main camera with a variable aperture, a 48 MP 4x periscope telephoto and a 40 MP ultra wide, 100 W "
                "wired and 80 W wireless charging, and IP68 and IP69. It runs EMUI without Google services."
            ),
            condition="average",
            condition_note=(
                "512 GB, Glazed Black, international version. Small scratches on the screen, not visible when it is "
                "on. Light wear on the camera ring. All cameras work. Battery health 91%. Phone and a USB-C cable."
            ),
            price=520,
        ),
    ),
    SeedListing(
        user=2,
        phone=PhoneCreate(
            model_code="SGT-LX9",
            model_name="Huawei Mate 80 Pro",
            os="android",
            camera_megapixels=50,
            battery_capacity=5750,
            display_size=6.75,
            description=(
                "Huawei Mate 80 Pro was released in November 2025 with the Kirin 9030 chip and a 6.75-inch LTPO OLED "
                "display. It has a 50 MP main camera with a variable aperture, a 48 MP 4x periscope telephoto and a 40 "
                "MP ultra wide, a 5750 mAh battery, 100 W wired and 80 W wireless charging, and IP68 and IP69."
            ),
            condition="like_new",
            condition_note=(
                "512 GB, Golden Black. Used for three months in a case with a screen protector. No scratches or dents. "
                "Battery health 99%. Full box with the charger."
            ),
            price=760,
        ),
    ),
    SeedListing(
        user=3,
        phone=PhoneCreate(
            model_code="VDE-AL00",
            model_name="Huawei Pura X",
            os="android",
            camera_megapixels=50,
            battery_capacity=4720,
            display_size=6.3,
            description=(
                "Huawei Pura X was released in China in March 2025 as a wide flip foldable with the Kirin 9020 chip, a "
                "6.3-inch main display and a 3.5-inch cover screen. It has a 50 MP main camera, a 40 MP ultra wide and "
                "an 8 MP 3.5x telephoto, 66 W wired and 40 W wireless charging. It runs HarmonyOS."
            ),
            condition="for_repair",
            condition_note=(
                "512 GB, White, China version. The hinge is loose and the main display has a dead pixel line along the "
                "fold. The cover screen, cameras and charging work. Sold for a hinge and display repair."
            ),
            price=300,
        ),
    ),
    SeedListing(
        user=4,
        phone=PhoneCreate(
            model_code="BKQ-N49",
            model_name="Honor Magic8 Pro",
            os="android",
            camera_megapixels=50,
            battery_capacity=7100,
            display_size=6.71,
            description=(
                "Honor Magic8 Pro was released in October 2025 with the Snapdragon 8 Elite Gen 5 chip and a 6.71-inch "
                "LTPO OLED display. It has a 50 MP main camera, a 200 MP 3.7x periscope telephoto and a 50 MP ultra "
                "wide, a 7100 mAh battery, 100 W wired and 80 W wireless charging, and IP68 and IP69."
            ),
            condition="like_new",
            condition_note=(
                "512 GB, Black, global version. Used for two months in a case. No scratches on the screen or the "
                "frame. Battery health 99%. Box, cable and the 100 W charger included."
            ),
            price=780,
        ),
    ),
    SeedListing(
        user=5,
        phone=PhoneCreate(
            model_code="MBH-N49",
            model_name="Honor Magic V5",
            os="android",
            camera_megapixels=50,
            battery_capacity=5820,
            display_size=7.95,
            description=(
                "Honor Magic V5 was released in July 2025 as a book-style foldable with the Snapdragon 8 Elite chip, a "
                "7.95-inch main display and a 6.43-inch cover screen, 8.8 mm thick when folded. It has a 50 MP main "
                "camera, a 64 MP 3x periscope telephoto and a 50 MP ultra wide, 66 W wired and 50 W wireless charging."
            ),
            condition="average",
            condition_note=(
                "512 GB, Ivory White, global version. Visible crease on the inner screen and light scratches on the "
                "cover screen. The hinge opens and closes normally. All cameras work. Battery health 90%. Phone and "
                "the original charger."
            ),
            price=690,
        ),
    ),
    SeedListing(
        user=6,
        phone=PhoneCreate(
            model_code="DNP-NX9",
            model_name="Honor 400 Pro",
            os="android",
            camera_megapixels=200,
            battery_capacity=6000,
            display_size=6.7,
            description=(
                "Honor 400 Pro was released in May 2025 with the Snapdragon 8 Gen 3 chip and a 6.7-inch 120 Hz AMOLED "
                "display. It has a 200 MP main camera, a 50 MP 3x telephoto and a 12 MP ultra wide, a 6000 mAh "
                "battery, 100 W wired and 50 W wireless charging, and IP68 and IP69."
            ),
            condition="for_repair",
            condition_note=(
                "512 GB, Lunar Grey. The phone does not charge: the USB-C port is damaged. Wireless charging works. "
                "The screen and all cameras are fine. Sold for a charging port replacement."
            ),
            price=160,
        ),
    ),
    SeedListing(
        user=0,
        phone=PhoneCreate(
            model_code="DNY-NX9",
            model_name="Honor 400",
            os="android",
            camera_megapixels=200,
            battery_capacity=6000,
            display_size=6.55,
            description=(
                "Honor 400 was released in May 2025 with the Snapdragon 7 Gen 3 chip and a 6.55-inch 120 Hz AMOLED "
                "display. It has a 200 MP main camera with OIS and a 12 MP ultra wide, a 6000 mAh battery and 80 W "
                "charging."
            ),
            condition="average",
            condition_note=(
                "256 GB, Desert Gold. Scuffs on the frame corners and a small chip on the back glass edge. Screen has "
                "no scratches. Cameras and charging work. Phone and a cable."
            ),
            price=230,
        ),
    ),
]
