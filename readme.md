# Formal Analysis of Search-and-Rescue Scenarios with UPPAAL

This repository contains the implementation, models, and report for a **Search-and-Rescue (SaR)** real‑time simulation built using **UPPAAL**. The goal of the project is to formally analyze the behavior and performance of autonomous and human agents involved in rescuing civilians in environments affected by fire.

The project was developed as part of the *Formal Methods for Concurrent and Real-Time Systems* course.

---

## 👥 Authors

- **Patrick Poggi**
- **Valentino Guerrini**  
- **Antonio Marusic**  

Instructors:  
- **Prof. Pierluigi San Pietro**  
- **Dr. Livia Lestingi**
  
---

## 📘 Project Overview

The simulation models a grid-based environment where:

- **Civilians** attempt to reach exits and may require rescue if exposed to fire.
- **First Responders (FRs)** move around the affected area to help endangered civilians.
- **Drones** patrol the environment, detecting civilians in need and coordinating rescue operations.
- **Fires and exits** form the hazard and goal structure of the map.

All interactions are implemented as *Timed Automata* and combined into a *Network of Timed Automata (NTA)* in UPPAAL.

A detailed report of the full model and its analysis is available in [`Report.pdf`](/doc/Report.pdf) .

---

## 🧩 Components

The complete model is composed of four UPPAAL templates:

### **1. Initialize**
Initializes the simulation grid by placing:
- Fires  
- Exits  
- Drones & their predefined paths  
- Civilians  
- First Responders  

After initialization, it broadcasts a synchronization signal to start the simulation.

---

### **2. Civilian**
Civilians:
- Move toward the closest exit using a greedy distance-based policy  
- Become **needy** if adjacent to fire  
- May become **casualties** after a time limit  
- Can be instructed by drones to:
  - Become **Zero Responders (ZRs)**
  - Contact First Responders  
- Can exit the map safely if adjacent to an exit

Stochastic extension:
- Civilians may **ignore drone instructions** with configurable probability.

---

### **3. First Responder**
First Responders:
- Patrol predefined circular paths around the fire  
- Detect needy civilians in their vicinity  
- Perform rescues within a specified time  
- May be contacted by civilians coordinated via drones  
- After completing a rescue, they resume their patrol from the victim’s position  

---

### **4. Drone**
Drones:
- Follow predefined flight paths  
- Scan surroundings for civilian pairs (one needy, one healthy)  
- Decide between:
  - Assigning Zero Responders  
  - Involving First Responders  
- Mark involved entities as *RESCUING* to avoid race conditions  

Stochastic extension:
- Drone sensors may **fail** with configurable probability, temporarily preventing detection.

---

## 📊 Properties and Verification

The UPPAAL model is verified using both:

### **Deterministic Queries**
Examples:
- *Is it possible to rescue ≥ N% of civilians within time T?*  
- *Is it guaranteed that at least N% survive within time T?*

### **Stochastic Queries (UPPAAL SMC)**
Examples:
- Probability that ≥ N% civilians are rescued  
- Expected number of rescued civilians  
- Distribution of drone sensor faults  
- Behavior under ignored instructions  

---

## 🧪 Experimental Scenarios

The project evaluates:

### **Scenario 1 — Small 10×10 Grid**
- Central fire  
- Semi-random civilian placement  
- Drones with moderate visibility  
- Demonstrates sensitivity to:
  - Drone visibility  
  - Rescue times  
  - Civilian reaction probabilities  

### **Scenario 2 — Larger 14×14 Grid**
- Irregular fire region  
- First Responders patrolling safely around fire  
- Lower probability of 100% rescue  
- Highlights:
  - Importance of drone assistance  
  - Stochastic variability  
  - Complex civilian–fire–drone interactions  

---

## 📄 Documentation

Included in this repository:

- **UPPAAL model files** (`.xml`)
- **Stochastic model versions**
- **Visualization charts used for analysis**
- **Full project report**: [`Report.pdf`](/doc/Report.pdf) 

---

## 🚀 How to Run

### **Prerequisites**
- UPPAAL (standard version)  
- UPPAAL SMC (for stochastic models)

### **Steps**
1. Open the `.xml` model file in [`src`](/src) in UPPAAL.
2. Load verification queries.
3. Run deterministic or SMC queries as needed.
4. Optionally adjust parameters:
   - Number of civilians  
   - Grid layout  
   - Drone visibility  
   - Rescue durations  
   - Probabilities (SMC)  

---

## 📎 License
This project is released for educational use within the course *Formal Methods for Concurrent and Real-Time Systems*.  
Feel free to reference or build upon it for academic purposes.

