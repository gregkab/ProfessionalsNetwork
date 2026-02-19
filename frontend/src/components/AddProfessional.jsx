import { useState } from "react";
import api from "../api";

const INITIAL = {
  full_name: "",
  email: "",
  phone: "",
  job_title: "",
  company_name: "",
  source: "direct",
};

export default function AddProfessional({ onCreated }) {
  const [form, setForm] = useState(INITIAL);
  const [status, setStatus] = useState(null);
  const [errors, setErrors] = useState(null);
  const [submitting, setSubmitting] = useState(false);

  const handleChange = (e) => {
    setForm({ ...form, [e.target.name]: e.target.value });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setSubmitting(true);
    setStatus(null);
    setErrors(null);
    try {
      await api.post("/professionals/", form);
      setStatus("Professional added successfully.");
      setForm(INITIAL);
      onCreated?.();
    } catch (err) {
      if (err.response?.data) {
        setErrors(err.response.data);
      } else {
        setErrors({ detail: "An unexpected error occurred." });
      }
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="card">
      <h2>Add Professional</h2>
      <form onSubmit={handleSubmit}>
        <div className="form-grid">
          <label>
            <span>Full Name *</span>
            <input
              name="full_name"
              value={form.full_name}
              onChange={handleChange}
              required
            />
          </label>
          <label>
            <span>Email</span>
            <input
              name="email"
              type="email"
              value={form.email}
              onChange={handleChange}
            />
          </label>
          <label>
            <span>Phone</span>
            <input name="phone" value={form.phone} onChange={handleChange} />
          </label>
          <label>
            <span>Job Title</span>
            <input
              name="job_title"
              value={form.job_title}
              onChange={handleChange}
            />
          </label>
          <label>
            <span>Company Name</span>
            <input
              name="company_name"
              value={form.company_name}
              onChange={handleChange}
            />
          </label>
          <label>
            <span>Source *</span>
            <select name="source" value={form.source} onChange={handleChange}>
              <option value="direct">Direct</option>
              <option value="partner">Partner</option>
              <option value="internal">Internal</option>
            </select>
          </label>
        </div>
        <button type="submit" disabled={submitting}>
          {submitting ? "Submitting…" : "Add Professional"}
        </button>
      </form>
      {status && <p className="success">{status}</p>}
      {errors && (
        <div className="error">
          {typeof errors === "object"
            ? Object.entries(errors).map(([key, val]) => (
                <p key={key}>
                  <strong>{key}:</strong>{" "}
                  {Array.isArray(val) ? val.join(", ") : String(val)}
                </p>
              ))
            : String(errors)}
        </div>
      )}
    </div>
  );
}
