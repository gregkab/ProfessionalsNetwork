import { useEffect, useState } from "react";
import api from "../api";

export default function ProfessionalsList({ refreshKey }) {
  const [professionals, setProfessionals] = useState([]);
  const [sourceFilter, setSourceFilter] = useState("");
  const [loading, setLoading] = useState(false);

  const fetchData = async (source) => {
    setLoading(true);
    try {
      const params = source ? { source } : {};
      const res = await api.get("/professionals/", { params });
      setProfessionals(res.data);
    } catch {
      setProfessionals([]);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData(sourceFilter);
  }, [sourceFilter, refreshKey]);

  const handleFilterChange = (e) => {
    setSourceFilter(e.target.value);
  };

  return (
    <div className="card">
      <div className="list-header">
        <h2>Professionals</h2>
        <label className="filter-label">
          Filter by source:
          <select value={sourceFilter} onChange={handleFilterChange}>
            <option value="">All</option>
            <option value="direct">Direct</option>
            <option value="partner">Partner</option>
            <option value="internal">Internal</option>
          </select>
        </label>
      </div>

      {loading ? (
        <p className="loading">Loading…</p>
      ) : professionals.length === 0 ? (
        <p className="empty">No professionals found.</p>
      ) : (
        <div className="table-wrapper">
          <table>
            <thead>
              <tr>
                <th>Full Name</th>
                <th>Email</th>
                <th>Phone</th>
                <th>Job Title</th>
                <th>Company</th>
                <th>Source</th>
                <th>Created</th>
              </tr>
            </thead>
            <tbody>
              {professionals.map((p) => (
                <tr key={p.id}>
                  <td>{p.full_name}</td>
                  <td>{p.email || "—"}</td>
                  <td>{p.phone || "—"}</td>
                  <td>{p.job_title || "—"}</td>
                  <td>{p.company_name || "—"}</td>
                  <td>
                    <span className={`badge badge-${p.source}`}>
                      {p.source}
                    </span>
                  </td>
                  <td>{new Date(p.created_at).toLocaleDateString()}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
