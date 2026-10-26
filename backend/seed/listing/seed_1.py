"""Seed listings, part 1 of 3: 20 listings, one listing per model."""

from modules.phones.schemas import PhoneCreate
from seed.schemas import SeedListing

LISTINGS: list[SeedListing] = [
    SeedListing(
        user=0,
        phone=PhoneCreate(
            model_code="A2172",
            model_name="iPhone 12",
            os="ios",
            camera_megapixels=12,
            battery_capacity=2815,
            display_size=6.1,
            description=(
                "iPhone 12 was released in 2020 with the A14 Bionic chip, a 6.1-inch Super Retina XDR OLED display "
                "and a Ceramic Shield front. It has a dual 12 MP camera system (wide and ultra wide), 5G, MagSafe "
                "and a Lightning port."
            ),
            condition="average",
            condition_note=(
                "64 GB, Blue, unlocked. Battery health 81%. Light scratches on the screen, visible only when the "
                "display is off, and small scuffs on the aluminum frame corners. Face ID and all cameras work. "
                "Comes with a USB-C to Lightning cable, no box."
            ),
            price=175,
        ),
    ),
    SeedListing(
        user=1,
        phone=PhoneCreate(
            model_code="A2482",
            model_name="iPhone 13",
            os="ios",
            camera_megapixels=12,
            battery_capacity=3227,
            display_size=6.1,
            description=(
                "iPhone 13 was released in 2021 with the A15 Bionic chip and a 6.1-inch Super Retina XDR OLED "
                "display. It has a dual 12 MP camera system with sensor-shift stabilization on the wide camera, "
                "Cinematic mode video, 5G and MagSafe charging."
            ),
            condition="like_new",
            condition_note=(
                "128 GB, Midnight, unlocked. Battery health 92%. Always used with a case and a screen protector, no "
                "scratches or dents. Original box and cable included."
            ),
            price=285,
        ),
    ),
    SeedListing(
        user=2,
        phone=PhoneCreate(
            model_code="A2483",
            model_name="iPhone 13 Pro",
            os="ios",
            camera_megapixels=12,
            battery_capacity=3095,
            display_size=6.1,
            description=(
                "iPhone 13 Pro was released in 2021 with the A15 Bionic chip and a 6.1-inch ProMotion OLED display "
                "with a refresh rate up to 120 Hz. It has a triple 12 MP camera system with a 3x telephoto, a LiDAR "
                "scanner, ProRAW and ProRes video, and a stainless steel frame."
            ),
            condition="for_repair",
            condition_note=(
                "256 GB, Sierra Blue. The back glass is cracked across the camera area and Face ID does not work "
                "after a drop. The screen, all cameras, speakers and charging work. Battery health 78%. Sold for "
                "repair or parts."
            ),
            price=160,
        ),
    ),
    SeedListing(
        user=3,
        phone=PhoneCreate(
            model_code="A2484",
            model_name="iPhone 13 Pro Max",
            os="ios",
            camera_megapixels=12,
            battery_capacity=4352,
            display_size=6.7,
            description=(
                "iPhone 13 Pro Max was released in 2021 with the A15 Bionic chip and a 6.7-inch ProMotion OLED "
                "display up to 120 Hz. It has a triple 12 MP camera system with a 3x telephoto, a LiDAR scanner, "
                "macro photography and a stainless steel frame."
            ),
            condition="average",
            condition_note=(
                "256 GB, Graphite, unlocked. Battery health 84%. A few fine scratches on the screen and wear marks "
                "on the stainless steel edges. Everything works, including Face ID and MagSafe. Phone only."
            ),
            price=330,
        ),
    ),
    SeedListing(
        user=4,
        phone=PhoneCreate(
            model_code="A2595",
            model_name="iPhone SE (3rd generation)",
            os="ios",
            camera_megapixels=12,
            battery_capacity=2018,
            display_size=4.7,
            description=(
                "iPhone SE (3rd generation) was released in 2022 with the A15 Bionic chip, a 4.7-inch Retina HD LCD "
                "display and a Home button with Touch ID. It has a single 12 MP wide camera, 5G and a Lightning port."
            ),
            condition="like_new",
            condition_note=(
                "64 GB, Starlight, unlocked. Battery health 95%. Bought as a backup phone and barely used, no "
                "scratches. Touch ID works. Original box and cable included."
            ),
            price=150,
        ),
    ),
    SeedListing(
        user=5,
        phone=PhoneCreate(
            model_code="A2649",
            model_name="iPhone 14",
            os="ios",
            camera_megapixels=12,
            battery_capacity=3279,
            display_size=6.1,
            description=(
                "iPhone 14 was released in 2022 with the A15 Bionic chip with a 5-core GPU and a 6.1-inch Super "
                "Retina XDR OLED display. It has a dual 12 MP camera system, Action mode video, Crash Detection and "
                "Emergency SOS via satellite. The US model is eSIM only."
            ),
            condition="average",
            condition_note=(
                "128 GB, Purple, unlocked. Battery health 86%. Small dent on the bottom edge near the Lightning "
                "port and light scratches on the back glass. Screen has no scratches. All functions work."
            ),
            price=270,
        ),
    ),
    SeedListing(
        user=6,
        phone=PhoneCreate(
            model_code="A2632",
            model_name="iPhone 14 Plus",
            os="ios",
            camera_megapixels=12,
            battery_capacity=4325,
            display_size=6.7,
            description=(
                "iPhone 14 Plus was released in 2022 with the A15 Bionic chip with a 5-core GPU and a 6.7-inch Super "
                "Retina XDR OLED display. It has a dual 12 MP camera system, Crash Detection, Emergency SOS via "
                "satellite and the longest battery life of the iPhone 14 lineup."
            ),
            condition="like_new",
            condition_note=(
                "256 GB, Midnight, unlocked. Battery health 90%. Used with a case and a screen protector from day one, "
                "no visible marks. Original box included."
            ),
            price=360,
        ),
    ),
    SeedListing(
        user=0,
        phone=PhoneCreate(
            model_code="A2650",
            model_name="iPhone 14 Pro",
            os="ios",
            camera_megapixels=48,
            battery_capacity=3200,
            display_size=6.1,
            description=(
                "iPhone 14 Pro was released in 2022 with the A16 Bionic chip and a 6.1-inch ProMotion OLED display "
                "with Dynamic Island and Always-On display. It has a 48 MP main camera, a 12 MP ultra wide and a "
                "12 MP 3x telephoto, and a stainless steel frame."
            ),
            condition="for_repair",
            condition_note=(
                "128 GB, Deep Purple. Green vertical line on the display and the touch does not respond in the top "
                "right corner. Cameras, Face ID and charging work. Battery health 80%. iCloud is signed out, the "
                "phone is ready for a screen replacement."
            ),
            price=190,
        ),
    ),
    SeedListing(
        user=1,
        phone=PhoneCreate(
            model_code="A2651",
            model_name="iPhone 14 Pro Max",
            os="ios",
            camera_megapixels=48,
            battery_capacity=4323,
            display_size=6.7,
            description=(
                "iPhone 14 Pro Max was released in 2022 with the A16 Bionic chip and a 6.7-inch ProMotion OLED "
                "display with Dynamic Island and Always-On display. It has a 48 MP main camera, a 12 MP ultra wide "
                "and a 12 MP 3x telephoto, Crash Detection and Emergency SOS via satellite."
            ),
            condition="average",
            condition_note=(
                "256 GB, Space Black, unlocked. Battery was replaced at an Apple Store, health 100%. Scratches on the "
                "frame and one small chip on the back glass corner. Screen is clean. Works perfectly."
            ),
            price=450,
        ),
    ),
    SeedListing(
        user=2,
        phone=PhoneCreate(
            model_code="A2846",
            model_name="iPhone 15",
            os="ios",
            camera_megapixels=48,
            battery_capacity=3349,
            display_size=6.1,
            description=(
                "iPhone 15 was released in 2023 with the A16 Bionic chip and a 6.1-inch Super Retina XDR OLED "
                "display with Dynamic Island. It has a 48 MP main camera with 2x optical-quality zoom, a 12 MP ultra "
                "wide camera and a USB-C port."
            ),
            condition="like_new",
            condition_note=(
                "128 GB, Pink, unlocked. Battery health 94%, 210 charge cycles. No scratches, kept in a case. Box and "
                "the original braided USB-C cable included."
            ),
            price=410,
        ),
    ),
    SeedListing(
        user=3,
        phone=PhoneCreate(
            model_code="A2847",
            model_name="iPhone 15 Plus",
            os="ios",
            camera_megapixels=48,
            battery_capacity=4383,
            display_size=6.7,
            description=(
                "iPhone 15 Plus was released in 2023 with the A16 Bionic chip and a 6.7-inch Super Retina XDR OLED "
                "display with Dynamic Island. It has a 48 MP main camera, a 12 MP ultra wide camera, a USB-C port "
                "and a color-infused matte glass back."
            ),
            condition="average",
            condition_note=(
                "128 GB, Green, unlocked. Battery health 87%. Several light scratches on the screen and scuffs on the "
                "aluminum frame. No cracks. All functions work. Phone and a USB-C cable."
            ),
            price=400,
        ),
    ),
    SeedListing(
        user=4,
        phone=PhoneCreate(
            model_code="A2848",
            model_name="iPhone 15 Pro",
            os="ios",
            camera_megapixels=48,
            battery_capacity=3274,
            display_size=6.1,
            description=(
                "iPhone 15 Pro was released in 2023 with the A17 Pro chip, a titanium frame and a 6.1-inch ProMotion "
                "OLED display with Always-On display. It has a 48 MP main camera, a 12 MP 3x telephoto, the Action "
                "button and a USB-C port with USB 3 speeds. It supports Apple Intelligence."
            ),
            condition="like_new",
            condition_note=(
                "256 GB, Natural Titanium, unlocked. Battery health 91%. No scratches on the screen or the titanium "
                "frame, always in a case. Original box included."
            ),
            price=540,
        ),
    ),
    SeedListing(
        user=5,
        phone=PhoneCreate(
            model_code="A2849",
            model_name="iPhone 15 Pro Max",
            os="ios",
            camera_megapixels=48,
            battery_capacity=4422,
            display_size=6.7,
            description=(
                "iPhone 15 Pro Max was released in 2023 with the A17 Pro chip, a titanium frame and a 6.7-inch "
                "ProMotion OLED display. It has a 48 MP main camera, a 12 MP ultra wide and a 12 MP 5x tetraprism "
                "telephoto, the Action button and a USB-C port with USB 3 speeds."
            ),
            condition="for_repair",
            condition_note=(
                "256 GB, Blue Titanium. The phone does not charge through the USB-C port, wireless MagSafe charging "
                "still works. The screen has a crack in the lower left corner, touch works. Battery health 83%. "
                "No other issues."
            ),
            price=330,
        ),
    ),
    SeedListing(
        user=6,
        phone=PhoneCreate(
            model_code="A3081",
            model_name="iPhone 16",
            os="ios",
            camera_megapixels=48,
            battery_capacity=3561,
            display_size=6.1,
            description=(
                "iPhone 16 was released in 2024 with the A18 chip and a 6.1-inch Super Retina XDR OLED display with "
                "Dynamic Island. It has a 48 MP Fusion main camera, a 12 MP ultra wide camera with macro, the Action "
                "button, Camera Control and Apple Intelligence support."
            ),
            condition="average",
            condition_note=(
                "128 GB, Ultramarine, unlocked. Battery health 89%. Light scratches on the screen and a scuff on the "
                "top left corner of the frame. Everything works, including Camera Control. Phone only."
            ),
            price=480,
        ),
    ),
    SeedListing(
        user=0,
        phone=PhoneCreate(
            model_code="A3082",
            model_name="iPhone 16 Plus",
            os="ios",
            camera_megapixels=48,
            battery_capacity=4674,
            display_size=6.7,
            description=(
                "iPhone 16 Plus was released in 2024 with the A18 chip and a 6.7-inch Super Retina XDR OLED display "
                "with Dynamic Island. It has a 48 MP Fusion main camera, a 12 MP ultra wide camera, Camera Control, "
                "the Action button and Apple Intelligence support."
            ),
            condition="like_new",
            condition_note=(
                "256 GB, Teal, unlocked. Battery health 96%. Under one year of use, screen protector since day one, "
                "no marks. Box, cable and the receipt included."
            ),
            price=590,
        ),
    ),
    SeedListing(
        user=1,
        phone=PhoneCreate(
            model_code="A3083",
            model_name="iPhone 16 Pro",
            os="ios",
            camera_megapixels=48,
            battery_capacity=3582,
            display_size=6.3,
            description=(
                "iPhone 16 Pro was released in 2024 with the A18 Pro chip, a titanium frame and a 6.3-inch ProMotion "
                "OLED display. It has a 48 MP Fusion main camera, a 48 MP ultra wide and a 12 MP 5x telephoto, "
                "4K 120 fps Dolby Vision video and Camera Control."
            ),
            condition="average",
            condition_note=(
                "256 GB, Desert Titanium, unlocked. Battery health 88%. Small scratches on the titanium edges and one "
                "visible scratch on the screen near the Dynamic Island. All cameras and Face ID work. Phone and "
                "USB-C cable."
            ),
            price=650,
        ),
    ),
    SeedListing(
        user=2,
        phone=PhoneCreate(
            model_code="A3084",
            model_name="iPhone 16 Pro Max",
            os="ios",
            camera_megapixels=48,
            battery_capacity=4685,
            display_size=6.9,
            description=(
                "iPhone 16 Pro Max was released in 2024 with the A18 Pro chip, a titanium frame and a 6.9-inch "
                "ProMotion OLED display. It has a 48 MP Fusion main camera, a 48 MP ultra wide and a 12 MP 5x "
                "telephoto, Camera Control and the longest battery life of the iPhone 16 lineup."
            ),
            condition="like_new",
            condition_note=(
                "512 GB, Black Titanium, unlocked. Battery health 93%. AppleCare+ active until December 2026. "
                "No scratches, always in a case. Full box with the original cable."
            ),
            price=860,
        ),
    ),
    SeedListing(
        user=3,
        phone=PhoneCreate(
            model_code="A3212",
            model_name="iPhone 16e",
            os="ios",
            camera_megapixels=48,
            battery_capacity=3961,
            display_size=6.1,
            description=(
                "iPhone 16e was released in February 2025 with the A18 chip, the Apple C1 modem and a 6.1-inch Super "
                "Retina XDR OLED display with a notch. It has a single 48 MP Fusion camera, Face ID, the Action "
                "button, a USB-C port and Apple Intelligence support. It has no MagSafe."
            ),
            condition="for_repair",
            condition_note=(
                "128 GB, White. The phone fell into water and the earpiece speaker is quiet and distorted, the bottom "
                "speaker and the microphone work. Face ID works. No cracks. Battery health 90%. Sold as is for repair."
            ),
            price=220,
        ),
    ),
    SeedListing(
        user=4,
        phone=PhoneCreate(
            model_code="A3258",
            model_name="iPhone 17",
            os="ios",
            camera_megapixels=48,
            battery_capacity=3692,
            display_size=6.3,
            description=(
                "iPhone 17 was released in September 2025 with the A19 chip and a 6.3-inch ProMotion OLED display "
                "with a refresh rate up to 120 Hz and Always-On display. It has a 48 MP Fusion main camera, a 48 MP "
                "ultra wide camera and an 18 MP Center Stage front camera. The US model is eSIM only."
            ),
            condition="like_new",
            condition_note=(
                "256 GB, Lavender, unlocked. Battery health 99%. Bought in August 2026, used for two months with a "
                "case and a screen protector. Full box included."
            ),
            price=690,
        ),
    ),
    SeedListing(
        user=5,
        phone=PhoneCreate(
            model_code="A3256",
            model_name="iPhone 17 Pro",
            os="ios",
            camera_megapixels=48,
            battery_capacity=4252,
            display_size=6.3,
            description=(
                "iPhone 17 Pro was released in September 2025 with the A19 Pro chip, an aluminum unibody with a vapor "
                "chamber cooling system and a 6.3-inch ProMotion OLED display. It has three 48 MP rear cameras: "
                "Fusion main, ultra wide and a 4x telephoto. The US model is eSIM only."
            ),
            condition="average",
            condition_note=(
                "256 GB, Cosmic Orange, unlocked. Battery health 95%. Scuffs on the aluminum corners and a light "
                "scratch on the camera plateau. Screen is clean. Everything works. Phone and cable only."
            ),
            price=820,
        ),
    ),
]
