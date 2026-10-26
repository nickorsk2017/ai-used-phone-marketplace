"""Seed listings, part 5 of 5: 16 listings of Oppo, vivo, Realme, Nothing and CMF, one listing per model."""

from modules.phones.schemas import PhoneCreate
from seed.schemas import SeedListing

LISTINGS: list[SeedListing] = [
    SeedListing(
        user=1,
        phone=PhoneCreate(
            model_code="PKJ110",
            model_name="Oppo Find X8 Ultra",
            os="android",
            camera_megapixels=50,
            battery_capacity=6100,
            display_size=6.82,
            description=(
                "Oppo Find X8 Ultra was released in China in April 2025 with the Snapdragon 8 Elite chip and a "
                "6.82-inch QHD+ LTPO AMOLED display. It has a Hasselblad quad camera with a 50 MP 1-inch main sensor, "
                "two 50 MP periscope telephotos at 3x and 6x and a 50 MP ultra wide, a 6100 mAh battery, 100 W wired "
                "and 50 W wireless charging, and IP68 and IP69. It runs ColorOS."
            ),
            condition="average",
            condition_note=(
                "512 GB, Moonlight Titanium, China version. Light scratches on the frame and the camera island. Screen "
                "is clean. All cameras work. Battery health 90%. Phone and the original charger."
            ),
            price=610,
        ),
    ),
    SeedListing(
        user=2,
        phone=PhoneCreate(
            model_code="CPH2791",
            model_name="Oppo Find X9 Pro",
            os="android",
            camera_megapixels=50,
            battery_capacity=7500,
            display_size=6.78,
            description=(
                "Oppo Find X9 Pro was released in October 2025 with the MediaTek Dimensity 9500 chip and a 6.78-inch "
                "LTPO AMOLED display. It has a Hasselblad triple camera with a 50 MP main, a 200 MP 3x periscope "
                "telephoto and a 50 MP ultra wide, a 7500 mAh battery, 80 W wired and 50 W wireless charging, and IP68 "
                "and IP69."
            ),
            condition="like_new",
            condition_note=(
                "512 GB, Titanium Charcoal, global version. Used for three months in a case with a screen protector. "
                "No scratches. Battery health 99%. Full box with the 80 W charger."
            ),
            price=820,
        ),
    ),
    SeedListing(
        user=3,
        phone=PhoneCreate(
            model_code="CPH2797",
            model_name="Oppo Find X9",
            os="android",
            camera_megapixels=50,
            battery_capacity=7025,
            display_size=6.59,
            description=(
                "Oppo Find X9 was released in October 2025 with the MediaTek Dimensity 9500 chip and a 6.59-inch 120 "
                "Hz AMOLED display. It has a Hasselblad triple camera with a 50 MP main, a 50 MP 3x periscope "
                "telephoto and a 50 MP ultra wide, a 7025 mAh battery, 80 W wired and 50 W wireless charging, and IP68 "
                "and IP69."
            ),
            condition="average",
            condition_note=(
                "256 GB, Space Black, global version. Small scratches on the screen and wear on the frame edges. All "
                "cameras and wireless charging work. Battery health 93%. Phone only."
            ),
            price=520,
        ),
    ),
    SeedListing(
        user=4,
        phone=PhoneCreate(
            model_code="CPH2671",
            model_name="Oppo Find N5",
            os="android",
            camera_megapixels=50,
            battery_capacity=5600,
            display_size=8.12,
            description=(
                "Oppo Find N5 was released in February 2025 as a book-style foldable with the Snapdragon 8 Elite chip, "
                "an 8.12-inch main display and a 6.62-inch cover screen, 8.9 mm thick when folded. It has a 50 MP main "
                "camera, a 50 MP 3x periscope telephoto and an 8 MP ultra wide, 80 W wired and 50 W wireless charging."
            ),
            condition="for_repair",
            condition_note=(
                "512 GB, Cosmic Black, global version. The cover screen is cracked and does not respond to touch. The "
                "main foldable display, hinge and cameras work. Sold for a cover screen replacement."
            ),
            price=420,
        ),
    ),
    SeedListing(
        user=5,
        phone=PhoneCreate(
            model_code="V2514",
            model_name="vivo X300 Pro",
            os="android",
            camera_megapixels=50,
            battery_capacity=6510,
            display_size=6.78,
            description=(
                "vivo X300 Pro was released in October 2025 with the MediaTek Dimensity 9500 chip and a 6.78-inch LTPO "
                "AMOLED display. It has a ZEISS triple camera with a 50 MP main, a 200 MP 3.7x periscope telephoto and "
                "a 50 MP ultra wide, a 6510 mAh battery, 90 W wired and 40 W wireless charging, and IP68 and IP69."
            ),
            condition="average",
            condition_note=(
                "512 GB, Phantom Black, global version. Light scratches on the back glass and one scuff on the frame "
                "corner. Screen is clean. All cameras work. Battery health 94%. Phone and the original charger."
            ),
            price=760,
        ),
    ),
    SeedListing(
        user=6,
        phone=PhoneCreate(
            model_code="V2515",
            model_name="vivo X300",
            os="android",
            camera_megapixels=200,
            battery_capacity=6040,
            display_size=6.31,
            description=(
                "vivo X300 was released in October 2025 with the MediaTek Dimensity 9500 chip and a compact 6.31-inch "
                "LTPO AMOLED display. It has a ZEISS triple camera with a 200 MP main, a 50 MP 3x periscope telephoto "
                "and a 50 MP ultra wide, a 6040 mAh battery, 90 W wired and 40 W wireless charging, and IP68 and IP69."
            ),
            condition="like_new",
            condition_note=(
                "256 GB, Mist Blue, global version. Used for two months in a case with a screen protector. No marks. "
                "Battery health 99%. Box, cable and the charger included."
            ),
            price=640,
        ),
    ),
    SeedListing(
        user=0,
        phone=PhoneCreate(
            model_code="V2503",
            model_name="vivo X200 FE",
            os="android",
            camera_megapixels=50,
            battery_capacity=6500,
            display_size=6.31,
            description=(
                "vivo X200 FE was released in June 2025 with the MediaTek Dimensity 9300+ chip and a compact 6.31-inch "
                "LTPO AMOLED display. It has a ZEISS triple camera with a 50 MP main, a 50 MP 3x periscope telephoto "
                "and an 8 MP ultra wide, a 6500 mAh battery, 90 W charging and IP68 and IP69."
            ),
            condition="average",
            condition_note=(
                "256 GB, Frost Blue. Scratches on the screen, visible only when it is off, and light scuffs on the "
                "frame. Cameras and charging work. Battery health 92%. Phone and a cable."
            ),
            price=320,
        ),
    ),
    SeedListing(
        user=1,
        phone=PhoneCreate(
            model_code="V2511",
            model_name="vivo V60",
            os="android",
            camera_megapixels=50,
            battery_capacity=6500,
            display_size=6.77,
            description=(
                "vivo V60 was released in August 2025 with the Snapdragon 7 Gen 4 chip and a 6.77-inch 120 Hz AMOLED "
                "display. It has a ZEISS triple camera with a 50 MP main, a 50 MP 3x periscope telephoto and an 8 MP "
                "ultra wide, a 6500 mAh battery, 90 W charging and IP68 and IP69."
            ),
            condition="like_new",
            condition_note=(
                "256 GB, Mist Gray. Used for one month in a case. No scratches. Battery health 100%. Full box with the "
                "charger."
            ),
            price=300,
        ),
    ),
    SeedListing(
        user=2,
        phone=PhoneCreate(
            model_code="RMX5210",
            model_name="Realme GT 8 Pro",
            os="android",
            camera_megapixels=50,
            battery_capacity=7000,
            display_size=6.79,
            description=(
                "Realme GT 8 Pro was released in October 2025 with the Snapdragon 8 Elite Gen 5 chip and a 6.79-inch "
                "QHD+ 144 Hz AMOLED display. It has a Ricoh GR tuned triple camera with a 50 MP main, a 200 MP 3x "
                "periscope telephoto and a 50 MP ultra wide, a 7000 mAh battery, 120 W wired and 50 W wireless "
                "charging, and IP68 and IP69."
            ),
            condition="like_new",
            condition_note=(
                "512 GB, Diary White. Used for two months in a case. No scratches on the screen or the back. Battery "
                "health 99%. Box and the 120 W charger included."
            ),
            price=580,
        ),
    ),
    SeedListing(
        user=3,
        phone=PhoneCreate(
            model_code="RMX5061",
            model_name="Realme GT 7",
            os="android",
            camera_megapixels=50,
            battery_capacity=7000,
            display_size=6.78,
            description=(
                "Realme GT 7 was released in May 2025 with the MediaTek Dimensity 9400e chip and a 6.78-inch 120 Hz "
                "AMOLED display. It has a 50 MP main camera with OIS, a 50 MP 2x telephoto and an 8 MP ultra wide, a "
                "7000 mAh battery and 120 W charging."
            ),
            condition="average",
            condition_note=(
                "256 GB, IceSense Blue. Scuffs on the frame and small scratches on the screen. All cameras work. "
                "Battery still lasts close to two days. Phone and the original charger."
            ),
            price=300,
        ),
    ),
    SeedListing(
        user=4,
        phone=PhoneCreate(
            model_code="RMX5101",
            model_name="Realme 15 Pro",
            os="android",
            camera_megapixels=50,
            battery_capacity=7000,
            display_size=6.8,
            description=(
                "Realme 15 Pro was released in July 2025 with the Snapdragon 7 Gen 4 chip and a 6.8-inch 144 Hz AMOLED "
                "display. It has a 50 MP main camera with OIS and a 50 MP ultra wide, a 7000 mAh battery, 80 W "
                "charging and IP68 and IP69."
            ),
            condition="for_repair",
            condition_note=(
                "256 GB, Flowing Silver. The screen is cracked in the top corner and the front camera does not focus. "
                "Touch, rear cameras and charging work. Sold for a display and front camera replacement."
            ),
            price=110,
        ),
    ),
    SeedListing(
        user=5,
        phone=PhoneCreate(
            model_code="A024",
            model_name="Nothing Phone (3)",
            os="android",
            camera_megapixels=50,
            battery_capacity=5150,
            display_size=6.67,
            description=(
                "Nothing Phone (3) was released in July 2025 with the Snapdragon 8s Gen 4 chip and a 6.67-inch 120 Hz "
                "OLED display. It has a triple camera with a 50 MP main, a 50 MP 3x periscope telephoto and a 50 MP "
                "ultra wide, 65 W wired and 15 W wireless charging, the Glyph Matrix LED display on the back and IP68."
            ),
            condition="average",
            condition_note=(
                "256 GB, Black, unlocked. Light scratches on the back glass and the frame corners. Screen is clean. "
                "The Glyph Matrix and all cameras work. Battery health 92%. Phone and a USB-C cable."
            ),
            price=380,
        ),
    ),
    SeedListing(
        user=6,
        phone=PhoneCreate(
            model_code="A059",
            model_name="Nothing Phone (3a)",
            os="android",
            camera_megapixels=50,
            battery_capacity=5000,
            display_size=6.77,
            description=(
                "Nothing Phone (3a) was released in March 2025 with the Snapdragon 7s Gen 3 chip and a 6.77-inch 120 "
                "Hz AMOLED display. It has a 50 MP main camera, a 50 MP 2x telephoto and an 8 MP ultra wide, a 5000 "
                "mAh battery, 50 W charging, Glyph lights and IP64."
            ),
            condition="for_repair",
            condition_note=(
                "128 GB, White. The phone fell into water: the speaker is muffled and the Glyph lights do not turn on. "
                "The screen, cameras and charging work. Sold for a speaker and Glyph repair."
            ),
            price=90,
        ),
    ),
    SeedListing(
        user=0,
        phone=PhoneCreate(
            model_code="A059P",
            model_name="Nothing Phone (3a) Pro",
            os="android",
            camera_megapixels=50,
            battery_capacity=5000,
            display_size=6.77,
            description=(
                "Nothing Phone (3a) Pro was released in March 2025 with the Snapdragon 7s Gen 3 chip and a 6.77-inch "
                "120 Hz AMOLED display. It has a 50 MP main camera, a 50 MP 3x periscope telephoto and an 8 MP ultra "
                "wide, a 5000 mAh battery, 50 W charging, Glyph lights and IP64."
            ),
            condition="average",
            condition_note=(
                "256 GB, Grey. Small scratches on the screen and the back. Cameras, Glyph lights and charging work. "
                "Battery health 90%. Phone and the original case."
            ),
            price=250,
        ),
    ),
    SeedListing(
        user=1,
        phone=PhoneCreate(
            model_code="A001",
            model_name="CMF Phone 2 Pro",
            os="android",
            camera_megapixels=50,
            battery_capacity=5000,
            display_size=6.77,
            description=(
                "CMF Phone 2 Pro by Nothing was released in May 2025 with the MediaTek Dimensity 7300 Pro chip and a "
                "6.77-inch 120 Hz AMOLED display. It has a 50 MP main camera, a 50 MP 2x telephoto and an 8 MP ultra "
                "wide, a 5000 mAh battery, 33 W charging and a removable back cover with accessory mounts."
            ),
            condition="like_new",
            condition_note=(
                "256 GB, Light Green. Used for one month. No scratches. Battery health 100%. Box, cable and the "
                "lanyard accessory included."
            ),
            price=160,
        ),
    ),
    SeedListing(
        user=2,
        phone=PhoneCreate(
            model_code="A069",
            model_name="Nothing Phone (4a)",
            os="android",
            camera_megapixels=50,
            battery_capacity=5080,
            display_size=6.78,
            description=(
                "Nothing Phone (4a) was released in March 2026 with the Snapdragon 7s Gen 4 chip and a 6.78-inch 120 "
                "Hz AMOLED display. It has a 50 MP main camera, a 50 MP 3.5x periscope telephoto and an 8 MP ultra "
                "wide, a 5080 mAh battery, 50 W charging and Glyph lights."
            ),
            condition="like_new",
            condition_note=(
                "256 GB, Black. Bought in April 2026, used in a case with a screen protector. No marks. Battery health "
                "100%. Full box."
            ),
            price=300,
        ),
    ),
]
