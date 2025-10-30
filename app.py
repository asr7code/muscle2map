import streamlit as st
import pandas as pd
import time
import copy  # <-- NEW: We'll need this to avoid changing old plans

# --- Page Configuration ---
st.set_page_config(
    layout="wide",
    page_title="MuscleMap AI",
    page_icon="💪"
)

# --- Sidebar ---
with st.sidebar:
    st.title("MuscleMap AI 💪")
    st.markdown("Your AI-Powered Fitness Transformation Companion.")
    st.markdown("---")
    st.markdown("**Project By:**")
    st.markdown("Paramjit Singh (2228947)")
    st.markdown("Rahul Rana (2228955)")
    st.markdown("**Mentor:**")
    st.markdown("Er. Aditya Sharma")
    st.markdown("---")

# --- AI Adaptation Engine (The "Brain") ---
# This is our Stage 1 "Rule-Based AI" as described in the synopsis.

def get_ai_recommendation(profile, progress):
    """
    Analyzes user profile and progress to generate a new plan.
    This is the core "AI" logic.
    """
    goal = profile['goal']
    experience = profile['experience_level'] # <-- NEW: AI now knows the user's experience
    time_interval_weeks = profile['time_interval_weeks']
    start_weight = profile['start_weight']
    current_weight = progress['current_weight']
    
    # Get a *copy* of the last plan to modify
    new_plan = copy.deepcopy(st.session_state.current_plan)
    new_plan["plan_title"] = f"Adapted Plan (Check-in #{len(st.session_state.progress_history)})"

    # --- Logic for Weight Reduction ---
    if goal == "Weight Reduction":
        weight_lost = start_weight - current_weight
        target_loss_per_week = 0.5  # Target 0.5 kg/week
        expected_loss = target_loss_per_week * time_interval_weeks
        
        if weight_lost >= expected_loss:
            new_plan['ai_feedback'] = f"**AI Feedback:** Great job! You've lost {weight_lost:.1f} kg, meeting your target. We'll stick to a similar plan to keep the progress steady."
            # No changes needed, plan is working
            
        elif weight_lost > 0:
            new_plan['ai_feedback'] = f"**AI Feedback:** Good progress! You've lost {weight_lost:.1f} kg. To help you hit your next target, we will slightly increase your cardio."
            new_plan['plan_details']['cardio_minutes_per_session'] += 5  # <-- NEW: Specific adaptation
            
        else:
            new_plan['ai_feedback'] = f"**AI Feedback:** It looks like we didn't lose weight this period. Don't worry, this is common. We'll adjust your plan. Please double-check your diet logs and we will increase workout intensity."
            new_plan['diet_recommendation'] = "Let's try a 400-calorie deficit. Please track your food intake carefully."
            new_plan['plan_details']['cardio_minutes_per_session'] += 10 # <-- NEW: Specific adaptation
            
        return new_plan

    # --- Logic for Muscle Gain ---
    elif goal == "Muscle Gain":
        weight_gained = current_weight - start_weight
        target_gain_per_week = 0.25  # Target 0.25 kg/week
        expected_gain = target_gain_per_week * time_interval_weeks

        if weight_gained >= expected_gain:
            new_plan['ai_feedback'] = f"**AI Feedback:** Excellent work! You've gained {weight_gained:.1f} kg, right on target. We'll increase the weights or reps on your main lifts to continue progressing."
            new_plan['plan_details']['notes'] = "Focus on progressive overload: add +2.5kg or +1 rep to your main lifts." # <-- NEW
        else:
            new_plan['ai_feedback'] = f"**AI Feedback:** We've gained {weight_gained:.1f} kg. This is a solid start. To boost progress, let's slightly increase your calorie surplus and focus on lifting heavier."
            new_plan['diet_recommendation'] = "Let's try a 350-calorie surplus. Ensure you're hitting your protein target."

        return new_plan
        
    # --- Logic for General Fitness ---
    else:
        new_plan['ai_feedback'] = "**AI Feedback:** You've logged a check-in for 'General Fitness'. We'll keep the plan the same. Keep up the great consistency!"
        return new_plan

# --- Initial Plans (Before AI Adaptation) ---
def get_initial_plan(goal, experience): # <-- NEW: Now accepts experience
    
    # --- This is our new "Structured Plan" format ---
    # This is MUCH better than a simple text string
    
    plan = {
        "plan_title": "Initial Plan",
        "diet_recommendation": "Eat a balanced diet.",
        "ai_feedback": "**AI Feedback:** Welcome! Here is your starting plan. Stick to it and we'll check your progress soon.",
        "plan_details": {
            "type": "Full Body",
            "frequency_per_week": 3,
            "main_lifts": ["Squat", "Bench Press", "Row"],
            "sets_per_lift": 3,
            "reps_per_set": 10,
            "cardio_days_per_week": 2,
            "cardio_minutes_per_session": 20,
            "notes": "Focus on good form."
        }
    }

    if goal == "Weight Reduction":
        plan['plan_title'] = "Initial Plan: Weight Reduction"
        plan['diet_recommendation'] = "Start with a 300-calorie deficit. Focus on protein and vegetables."
        plan['plan_details']['cardio_days_per_week'] = 3
        plan['plan_details']['cardio_minutes_per_session'] = 30
        
        # <-- NEW: Logic for Experience Level -->
        if experience == "Intermediate":
            plan['plan_details']['reps_per_set'] = 12 # Higher reps
            plan['plan_details']['cardio_minutes_per_session'] = 35

    elif goal == "Muscle Gain":
        plan['plan_title'] = "Initial Plan: Muscle Gain"
        plan['diet_recommendation'] = "Start with a 250-calorie surplus. Eat 1.8g of protein per kg of bodyweight."
        plan['plan_details']['cardio_days_per_week'] = 0 # Focus on lifting
        plan['plan_details']['reps_per_set'] = 8  # Heavier weight
        
        # <-- NEW: Logic for Experience Level -->
        if experience == "Intermediate":
            plan['plan_details']['type'] = "Push-Pull-Legs"
            plan['plan_details']['frequency_per_week'] = 4
            plan['plan_details']['main_lifts'] = ["Bench Press", "Overhead Press", "Deadlift", "Squat"]
            plan['plan_details']['sets_per_lift'] = 4
            plan['plan_details']['reps_per_set'] = 6
        elif experience == "Advanced":
            plan['plan_title'] = "Initial Plan: Muscle Gain (Advanced)"
            plan['plan_details']['type'] = "Advanced PPL"
            plan['plan_details']['frequency_per_week'] = 6
            plan['plan_details']['sets_per_lift'] = 5
            plan['plan_details']['reps_per_set'] = 5 # Strength focus
            plan['plan_details']['notes'] = "Focus on compound lifts and progressive overload."

    else: # General Fitness
        plan['plan_title'] = "Initial Plan: General Fitness"
        if experience == "Beginner":
             plan['plan_details']['notes'] = "Welcome! Focus on learning the movements."

    return plan

# --- Streamlit App (The "Face") ---
st.title("Welcome to MuscleMap AI")

# Use st.session_state as a simple "database" to store user data
if 'user_profile' not in st.session_state:
    st.session_state.user_profile = None
    st.session_state.current_plan = None
    st.session_state.progress_history = []

# --- 1. Onboarding / Profile Creation ---
if st.session_state.user_profile is None:
    st.header("Let's create your profile to get started.")
    
    with st.form("profile_form"):
        st.write("Tell us about yourself:")
        age = st.number_input("Age", min_value=16, max_value=100, value=25)
        height = st.number_input("Height (cm)", min_value=100, max_value=250, value=170)
        start_weight = st.number_input("Current Weight (kg)", min_value=40.0, max_value=200.0, value=70.0, step=0.1)
        
        # <-- NEW: Added Experience Level -->
        experience_level = st.selectbox("What is your fitness experience?", 
                                        ("Beginner", "Intermediate", "Advanced"))
        
        st.write("What is your primary goal?")
        goal_options = ["Weight Reduction", "Muscle Gain", "General Fitness"]
        goal = st.selectbox("Goal", goal_options)
        
        time_interval_options = [2, 4, 6]
        time_interval_weeks = st.selectbox("How long is this goal interval?", time_interval_options, format_func=lambda x: f"{x} weeks")
        
        submitted = st.form_submit_button("Create My Profile & First Plan")
        
        if submitted:
            # Save the profile to our session_state "database"
            st.session_state.user_profile = {
                "age": age,
                "height": height,
                "start_weight": start_weight,
                "goal": goal,
                "time_interval_weeks": time_interval_weeks,
                "experience_level": experience_level  # <-- NEW
            }
            # Generate the user's first plan
            st.session_state.current_plan = get_initial_plan(goal, experience_level) # <-- NEW
            
            with st.spinner("Generating your personalized plan..."):
                time.sleep(2)
            
            st.success("Your profile and first plan are ready!")
            st.balloons()
            st.rerun()

# --- 2. Main Dashboard (After Onboarding) ---
else:
    profile = st.session_state.user_profile
    plan = st.session_state.current_plan
    
    st.header(f"Your Goal: {profile['goal']} ({profile['experience_level']})") # <-- NEW
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Your Current AI-Generated Plan")
        with st.container(border=True):
            st.markdown(f"### {plan['plan_title']}")
            st.markdown(plan['ai_feedback'])
            st.markdown("---")
            st.markdown(f"**Your Diet:**\n{plan['diet_recommendation']}")
            
            # <-- NEW: Displaying the new structured plan -->
            st.markdown(f"**Your Workout:**")
            details = plan['plan_details']
            st.markdown(f"- **Type:** {details['type']} ({details['frequency_per_week']} days/week)")
            st.markdown(f"- **Main Lifts:** {', '.join(details['main_lifts'])}")
            st.markdown(f"- **Structure:** {details['sets_per_lift']} sets of {details['reps_per_set']} reps")
            st.markdown(f"- **Cardio:** {details['cardio_days_per_week']} days/week for {details['cardio_minutes_per_session']} min")
            st.markdown(f"- **Notes:** {details['notes']}")
            # <-- End of new section -->

        st.subheader("Your Profile")
        with st.container(border=True):
            # <-- NEW: Changed to use "start_weight" as the "current" weight for this interval
            st.metric("Weight (Start of Interval)", f"{profile['start_weight']} kg")
            st.metric("Goal Interval", f"{profile['time_interval_weeks']} weeks")

    with col2:
        st.subheader("Log Your Progress")
        st.write(f"Your goal interval is {profile['time_interval_weeks']} weeks. When you're ready to check in, fill out the form below.")
        
        with st.form("progress_form"):
            current_weight = st.number_input("Your New Current Weight (kg)", min_value=40.0, max_value=200.0, value=profile['start_weight'], step=0.1)
            notes = st.text_area("How did the last period feel? (Optional)")
            
            submitted = st.form_submit_button("Analyze My Progress & Update My Plan")
            
            if submitted:
                # This is the "Core Loop" you described!
                
                # 1. Create a progress log
                progress_log = {
                    "current_weight": current_weight,
                    "notes": notes
                }
                
                # 2. Add to history
                st.session_state.progress_history.append(progress_log)
                
                with st.spinner("Analyzing your progress and generating new AI recommendations..."):
                    time.sleep(3)
                    
                    # 3. Call the "AI Brain" to get a new plan
                    new_plan = get_ai_recommendation(profile, progress_log)
                    
                    # 4. Update the user's plan in our "database"
                    st.session_state.current_plan = new_plan
                    
                    # 5. Update the user's "start_weight" for the *next* interval
                    st.session_state.user_profile['start_weight'] = current_weight
                
                st.success("Your plan has been updated by the AI!")
                st.balloons()
                st.rerun()

    # Display progress history
    if st.session_state.progress_history:
        st.subheader("Your Progress History")
        
        # Create a list of weights for the chart
        weight_history = [st.session_state.user_profile['start_weight']] # Add initial weight
        
        # <-- NEW: Fix for progress history logic -->
        # We need to get the "start_weight" *before* the current interval
        # This is tricky, let's just chart the logged weights.
        
        history_weights = [log['current_weight'] for log in st.session_state.progress_history]
        
        # Let's create a cleaner history for the table
        history_data = []
        # Find the very first weight
        first_weight = st.session_state.user_profile['start_weight']
        if st.session_state.progress_history:
             # This is a bit of a hack, but for session_state it's fine
             # We trace back the logs to find the original weight
             first_weight = st.session_state.progress_history[0]['current_weight'] - (st.session_state.progress_history[0]['current_weight'] - profile['start_weight'])
        
        history_data.append({"Check-in #": 0, "Weight (kg)": first_weight, "Notes": "Initial Profile"})
        
        for i, log in enumerate(st.session_state.progress_history):
            history_data.append({
                "Check-in #": i + 1,
                "Weight (kg)": log['current_weight'],
                "Notes": log.get('notes', 'N/A')
            })

        history_df = pd.DataFrame(history_data).set_index("Check-in #")
        
        st.dataframe(history_df, use_container_width=True)
        
        # Create a line chart of the weight
        chart_df = history_df.rename(columns={"Weight (kg)": "Weight"})
        st.line_chart(chart_df, y="Weight")

