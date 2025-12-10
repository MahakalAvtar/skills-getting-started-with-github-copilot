document.addEventListener("DOMContentLoaded", () => {
  const activitiesList = document.getElementById("activities-list");
  const activitySelect = document.getElementById("activity");
  const signupForm = document.getElementById("signup-form");
  const messageDiv = document.getElementById("message");

  // Function to fetch activities from API
  async function fetchActivities() {
    try {
      const response = await fetch("/activities");
      const activities = await response.json();

      // Clear loading message
      activitiesList.innerHTML = "";

      // Populate activities list
      Object.entries(activities).forEach(([name, details]) => {
        const activityCard = document.createElement("div");
        activityCard.className = "activity-card";

        const spotsLeft = details.max_participants - details.participants.length;

        // build card content (replaces the previous innerHTML approach)
        const title = document.createElement("h4");
        title.textContent = name;

        const desc = document.createElement("p");
        desc.textContent = details.description;

        const scheduleP = document.createElement("p");
        scheduleP.innerHTML = `<strong>Schedule:</strong> ${details.schedule}`;

        const availP = document.createElement("p");
        availP.innerHTML = `<strong>Availability:</strong> ${spotsLeft} spots left`;

        // Participants header
        const participantsLabel = document.createElement("p");
        participantsLabel.innerHTML = `<strong>Participants:</strong>`;

        // Helper to get initials
        function getInitials(fullName) {
          return (fullName || "")
            .split(" ")
            .map(part => part[0] || "")
            .slice(0, 2)
            .join("")
            .toUpperCase();
        }

        const participantsContainer = document.createElement("div");
        participantsContainer.className = "participants-list";

        if (!details.participants || details.participants.length === 0) {
          const empty = document.createElement("div");
          empty.className = "no-participants";
          empty.innerHTML = "<em>No participants yet</em>";
          participantsContainer.appendChild(empty);
        } else {
          details.participants.forEach((participant) => {
            const item = document.createElement("div");
            item.className = "participant";

            const avatar = document.createElement("div");
            avatar.className = "avatar";
            avatar.textContent = getInitials(participant);

            const nameNode = document.createElement("div");
            nameNode.className = "name";
            nameNode.textContent = participant;

            const deleteBtn = document.createElement("button");
            deleteBtn.className = "delete-btn";
            deleteBtn.innerHTML = "✕";
            deleteBtn.type = "button";
            deleteBtn.addEventListener("click", async (e) => {
              e.preventDefault();
              try {
                const response = await fetch(
                  `/activities/${encodeURIComponent(name)}/unregister?email=${encodeURIComponent(participant)}`,
                  {
                    method: "DELETE",
                  }
                );

                if (response.ok) {
                  fetchActivities();
                } else {
                  console.error("Failed to unregister participant");
                }
              } catch (error) {
                console.error("Error unregistering participant:", error);
              }
            });

            item.appendChild(avatar);
            item.appendChild(nameNode);
            item.appendChild(deleteBtn);
            participantsContainer.appendChild(item);
          });
        }

        // assemble card
        activityCard.appendChild(title);
        activityCard.appendChild(desc);
        activityCard.appendChild(scheduleP);
        activityCard.appendChild(availP);
        activityCard.appendChild(participantsLabel);
        activityCard.appendChild(participantsContainer);

        activitiesList.appendChild(activityCard);

        // Add option to select dropdown
        const option = document.createElement("option");
        option.value = name;
        option.textContent = name;
        activitySelect.appendChild(option);
      });
    } catch (error) {
      activitiesList.innerHTML = "<p>Failed to load activities. Please try again later.</p>";
      console.error("Error fetching activities:", error);
    }
  }

  // Handle form submission
  signupForm.addEventListener("submit", async (event) => {
    event.preventDefault();

    const email = document.getElementById("email").value;
    const activity = document.getElementById("activity").value;

    try {
      const response = await fetch(
        `/activities/${encodeURIComponent(activity)}/signup?email=${encodeURIComponent(email)}`,
        {
          method: "POST",
        }
      );

      const result = await response.json();

      if (response.ok) {
        messageDiv.textContent = result.message;
        messageDiv.className = "success";
        signupForm.reset();
        // Refresh activities list after successful signup
        await fetchActivities();
      } else {
        messageDiv.textContent = result.detail || "An error occurred";
        messageDiv.className = "error";
      }

      messageDiv.classList.remove("hidden");

      // Hide message after 5 seconds
      setTimeout(() => {
        messageDiv.classList.add("hidden");
      }, 5000);
    } catch (error) {
      messageDiv.textContent = "Failed to sign up. Please try again.";
      messageDiv.className = "error";
      messageDiv.classList.remove("hidden");
      console.error("Error signing up:", error);
    }
  });

  // Initialize app
  fetchActivities();
});
