import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";

function Dashboard() {

  const navigate = useNavigate();

  const [checking, setChecking] = useState(true);
  const [user, setUser] = useState(null);


  useEffect(() => {

    const storedUser =
      localStorage.getItem("user");


    if (!storedUser) {

      navigate("/");

      return;
    }


    try {

      const parsedUser =
        JSON.parse(storedUser);

      setUser(parsedUser);

    } catch (error) {

      console.error(error);

      localStorage.removeItem("user");

      navigate("/");

      return;
    }


    setChecking(false);

  }, [navigate]);


  const handleLogout = () => {

    localStorage.removeItem("user");

    navigate("/");

  };


  if (checking) {
    return <div>Loading...</div>;
  }


  return (

    <div className="dashboard-container">

      <header className="dashboard-header">

        <div>

          <h1>
            LearnSmart 📚
          </h1>

          <p>
            Your Adaptive Learning Coach
          </p>

        </div>


        <button
          onClick={handleLogout}
        >
          Log Out
        </button>

      </header>


      <main>

        {/* WELCOME */}

        <section className="welcome-card">

          <div>

            <p>Welcome back,</p>

            <h1>
              {user?.name || "Learner"}! 👋
            </h1>

            <p>
              Keep learning, keep growing!
            </p>

          </div>

        </section>


        {/* STATS */}

        <section className="stats-container">

          <div className="stat-card">

            <h3>
              Overall Progress
            </h3>

            <h2>
              65%
            </h2>

            <p>
              You're on track!
            </p>

          </div>


          <div className="stat-card">

            <h3>
              Completed Topics
            </h3>

            <h2>
              12 / 20
            </h2>

            <p>
              Keep going!
            </p>

          </div>


          <div className="stat-card">

            <h3>
              Hours Studied
            </h3>

            <h2>
              28 hrs
            </h2>

            <p>
              Great consistency!
            </p>

          </div>

        </section>


        {/* CURRENT TOPIC */}

        <section className="topic-card">

          <div>

            <p>
              CURRENT TOPIC
            </p>

            <h2>
              Fractions Multiplication
            </h2>

            <p>
              Your current progress: 58%
            </p>

          </div>


          <button
            onClick={() => navigate("/quiz")}
          >
            Continue Learning →
          </button>

        </section>


        {/* AI COACH */}

        <section className="ai-card">

          <div>

            <h2>
              🤖 AI Learning Coach
            </h2>

            <p>

              I noticed that you're having
              some difficulty with
              <strong>
                {" "}Fractions Multiplication.
              </strong>

            </p>

            <p>

              💡 Recommendation:
              Practice 5 reinforcement
              questions before advancing.

            </p>

          </div>


          <button
            onClick={() => navigate("/quiz")}
          >
            Get Started →
          </button>

        </section>


        {/* NEXT TOPIC */}

        <section className="next-topic-card">

          <div>

            <p>
              YOU'RE MAKING PROGRESS 🚀
            </p>

            <h2>
              Advance to the Next Topic
            </h2>

            <p>

              Complete the current practice
              and continue your learning journey.

            </p>

          </div>


          <button
            onClick={() => navigate("/quiz")}
          >
            Advance to Next Topic →
          </button>

        </section>


      </main>

    </div>
  );
}


export default Dashboard;