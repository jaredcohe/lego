from hub import port, light_matrix, light
import motor
import runloop
import distance_sensor

# --- Combination Target Ranges (in degrees) ---
# 1st turn: between 270 and 360
COMBO_1_MIN = -90
COMBO_1_MAX = -1

# 2nd turn: between 0 and 90
COMBO_2_MIN = 1
COMBO_2_MAX = 90

# 3rd turn: between 180 and 270
COMBO_3_MIN = -180
COMBO_3_MAX = -90

# How many degrees the lock motor will turn when unlocked.
LOCK_TURN_DEGREES = 90

# Time in milliseconds the user has for each step.
TIME_PER_STEP_MS = 3000

COMBO_MOTOR = port.B
LOCK_MOTOR = port.C
print("COMBO MOTOR: " + str(COMBO_MOTOR))
print("LOCK MOTOR: " + str(LOCK_MOTOR))

async def check_combination_step(step_number, min_angle, max_angle):
    """
    Checks a single step of the combination.
    Waits for a set time, reads the motor position, and checks if it's correct.
    Returns True if correct, False otherwise.
    """
    # Give the user time to turn the motor
    await runloop.sleep_ms(TIME_PER_STEP_MS)

    # Get the motor's data tuple and extract the relative position (the first value).
    # This value is then kept within a 0-359 degree circle.
    position = motor.absolute_position(COMBO_MOTOR)
    print("position: " + str(position))

    print("Step {} position entered: {} degrees.".format(step_number, position))

    if min_angle <= position <= max_angle:
        print("Step {} CORRECT.".format(step_number))
        light.color(1, 5)
        light_matrix.show_image(light_matrix.IMAGE_YES)
        await runloop.sleep_ms(1000)
        light_matrix.clear()
        return True
    else:
        print("Step {} INCORRECT. Expected {}-{}, got {}.".format(step_number, min_angle, max_angle, position))
        light_matrix.show_image(light_matrix.IMAGE_NO)
        light.color(1, 9)
        await runloop.sleep_ms(1000)
        light_matrix.clear()
        return False

async def main():
    motor.run_to_absolute_position(port.E, 95, 360)
    light.color(1, 5)
    x = 0
    while x < 100:
        await runloop.sleep_ms(1000)
        print(x)
        x = x + 1
        print(distance_sensor.distance(port.D))
        if (((distance_sensor.distance(port.D)) < 200) and ((distance_sensor.distance(port.D)) > 1)):
            motor.run_for_degrees(port.E, -90, 360)
            x = 100
            # Move combo motor to position 0
            motor.run_to_absolute_position(COMBO_MOTOR, 0, 360)
            motor_position = motor.absolute_position(COMBO_MOTOR)
            print("motor_position: " + str(motor_position))

            # --- Step 1 ---
            print("Enter 1st number ({}-{} degrees)...".format(COMBO_1_MIN, COMBO_1_MAX))
            if not await check_combination_step(1, COMBO_1_MIN, COMBO_1_MAX):
                print("Resetting lock.")
                runloop.run(main())
                return # End the program if incorrect

            # --- Step 2 ---
            print("\nEnter 2nd number ({}-{} degrees)...".format(COMBO_2_MIN, COMBO_2_MAX))
            if not await check_combination_step(2, COMBO_2_MIN, COMBO_2_MAX):
                print("Resetting lock.")
                runloop.run(main())
                return # End the program if incorrect

            # --- Step 3 ---
            print("\nEnter 3rd number ({} to {} degrees)...".format(COMBO_3_MIN, COMBO_3_MAX))
            if not await check_combination_step(3, COMBO_3_MIN, COMBO_3_MAX):
                print("Resetting lock.")
                runloop.run(main())
                return # End the program if incorrect

            # --- Success ---
            print("\n-------------------------")
            print("COMBINATION ACCEPTED!")
            light_matrix.show_image(light_matrix.IMAGE_HAPPY)
            print("Unlocking...")
            # Call the run_for_degrees method on the lock motor object
            await motor.run_for_degrees(LOCK_MOTOR, LOCK_TURN_DEGREES, 360)
            print("Unlocked.")

    print("DONE")

runloop.run(main())
