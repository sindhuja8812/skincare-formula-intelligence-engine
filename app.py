import streamlit as st

st.set_page_config(page_title="Skincare Formula Intelligence Engine", page_icon="🧴")

st.title("🧴 Skincare Formula Intelligence Engine")
st.write("Analyze and optimize your skincare formulas.")

with st.form("formula_form"):
    formula_input = st.text_area("Enter your formula ingredients", placeholder="e.g. Niacinamide 5%, Hyaluronic Acid 1%...")
    submitted = st.form_submit_button("Analyze")

if submitted:
    if not formula_input.strip():
        st.error("Please enter some ingredients.")
    else:
        st.success("Formula received!")
        # TODO: add analysis logic
        st.write(formula_input)
