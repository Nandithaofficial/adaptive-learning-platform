import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";

function Dashboard() {
  const [checking, setChecking] = useState(true);
  const navigate = useNavigate();

  useEffect(() => {
    const token = localStorage.getItem("token");
    if (!token) {
      navigate("/");
    } else {
      setChecking(false);
    }
  }, [navigate]);

  const handleLogout = () => {
    localStorage.removeItem("token");
    navigate("/");
  };

  if (checking) return null;

  return (
    <div className="dashboard-container">
      <header>
        <h1>Dashboard</h1>
        <button onClick={handleLogout}>Log Out</button>
      </header>

      <main>
        <p>Welcome back! Here's your overview.</p>
        <div className="dashboard-actions">
          <button onClick={() => navigate("/quiz")}>Start Quiz</button>
        </div>
      </main>
    </div>
  );
}

export default Dashboard;