import { useState } from "react";
import { useNavigate } from "react-router-dom";

const API_URL = "http://localhost:5001/api/auth";

function Login() {

  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");

  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const navigate = useNavigate();


  const handleSubmit = async (e) => {

    e.preventDefault();

    setError("");
    setLoading(true);

    try {

      const res = await fetch(`${API_URL}/login`, {

        method: "POST",

        headers: {
          "Content-Type": "application/json"
        },

        body: JSON.stringify({
          email: email,
          password: password
        })

      });


      const data = await res.json();


      if (!res.ok) {

        setError(
          data.message || "Login failed"
        );

        setLoading(false);

        return;
      }


      // Store logged-in user
      localStorage.setItem(
        "user",
        JSON.stringify(data.user)
      );


      // Go to dashboard
      navigate("/dashboard");


    } catch (err) {

      console.error(err);

      setError(
        "Cannot connect to server. Make sure the backend is running."
      );

    } finally {

      setLoading(false);

    }
  };


  return (

    <div className="auth-container">

      <form
        className="auth-form"
        onSubmit={handleSubmit}
      >

        <h1>Login</h1>


        {error && (
          <p className="error">
            {error}
          </p>
        )}


        <input
          type="email"
          placeholder="Email"
          value={email}
          onChange={(e) =>
            setEmail(e.target.value)
          }
          required
        />


        <input
          type="password"
          placeholder="Password"
          value={password}
          onChange={(e) =>
            setPassword(e.target.value)
          }
          required
        />


        <button
          type="submit"
          disabled={loading}
        >

          {loading ? "Logging in..." : "Log In"}

        </button>


        <p>

          Don't have an account?{" "}

          <button
            type="button"
            className="link-button"
            onClick={() => navigate("/signup")}
          >
            Sign up
          </button>

        </p>

      </form>

    </div>
  );
}


export default Login;