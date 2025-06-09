from hub import port
import motor # Still needed for motor-specific constants if used
import time
import runloop

# --- Combination Target Ranges (in degrees) ---
# 1st turn: between 260 and 330 degrees
COMBO_1_MIN = -90
COMBO_1_MAX = -1

# 2nd turn: between 40 and 120 degrees
COMBO_2_MIN = 1
COMBO_2_MAX = 90

# 3rd turn: between 320 and 360 degrees.
COMBO_3_MIN = -180
COMBO_3_MAX = -90

# --- Lock Action ---
# How many degrees the lock motor will turn when unlocked.
LOCK_TURN_DEGREES = 90

# --- Timing ---
# Time in milliseconds the user has for each step.
TIME_PER_STEP_MS = 5000

COMBO_MOTOR = port.B
LOCK_MOTOR = port.C
print("COMBO MOTOR: " + str(COMBO_MOTOR))
print("LOCK MOTOR: " + str(LOCK_MOTOR))

async def check_combination_step(step_number, min_angle, max_angle):
    """
    Checks a single step of the combination.
    Waits for a set time, reads the motor position, and checks if it's correct.
    Requires the motor object to be passed to it.
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
        return True
    else:
        print("Step {} INCORRECT. Expected {}-{}, got {}.".format(step_number, min_angle, max_angle, position))
        return False

async def main():
    # Move combo motor to position 0
    motor.run_to_absolute_position(COMBO_MOTOR, 0, 360)
    motor_position = motor.absolute_position(COMBO_MOTOR)
    print("motor_position: " + str(motor_position))

    # --- Step 1 ---
    print("Enter 1st number ({}-{} degrees)...".format(COMBO_1_MIN, COMBO_1_MAX))
    if not await check_combination_step(1, COMBO_1_MIN, COMBO_1_MAX):
        print("Resetting lock.")
        return # End the program if incorrect

    # --- Step 2 ---
    print("\nEnter 2nd number ({}-{} degrees)...".format(COMBO_2_MIN, COMBO_2_MAX))
    if not await check_combination_step(2, COMBO_2_MIN, COMBO_2_MAX):
        print("Resetting lock.")
        return # End the program if incorrect

    # --- Step 3 ---
    print("\nEnter 3rd number ({} to {} degrees)...".format(COMBO_3_MIN, COMBO_3_MAX))
    if not await check_combination_step(3, COMBO_3_MIN, COMBO_3_MAX):
        print("Resetting lock.")
        return # End the program if incorrect

    # --- Success ---
    print("\n-------------------------")
    print("COMBINATION ACCEPTED!")
    print("Unlocking...")
    # Call the run_for_degrees method on the lock motor object
    await motor.run_for_degrees(LOCK_MOTOR, LOCK_TURN_DEGREES, 360)
    print("Unlocked.")

runloop.run(main())
