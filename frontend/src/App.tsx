import { FormEvent, useEffect, useState } from "react";

type Screen = "signin" | "dashboard" | "processing" | "results";
type StudentStatus = "present" | "absent" | "review";

const classPhoto =
  "https://images.unsplash.com/photo-1577896851231-70ef18881754?crop=entropy&cs=tinysrgb&fit=crop&fm=jpg&q=86&w=1400";

const students: {
  roll: string;
  name: string;
  status: StudentStatus;
  match: string;
}[] = [
  { roll: "01", name: "Aarav Mehta", status: "present", match: "98%" },
  { roll: "02", name: "Aditi Nair", status: "present", match: "96%" },
  { roll: "03", name: "Ananya Iyer", status: "review", match: "61%" },
  { roll: "04", name: "Arjun Sharma", status: "present", match: "95%" },
  { roll: "05", name: "Diya Patel", status: "absent", match: "—" },
  { roll: "06", name: "Ishaan Verma", status: "present", match: "93%" },
  { roll: "07", name: "Kabir Singh", status: "present", match: "97%" },
  { roll: "08", name: "Kavya Reddy", status: "present", match: "91%" },
  { roll: "09", name: "Meera Joshi", status: "absent", match: "—" },
  { roll: "10", name: "Nisha Kulkarni", status: "present", match: "94%" },
  { roll: "11", name: "Pranav Rao", status: "review", match: "58%" },
  { roll: "12", name: "Riya Kapoor", status: "present", match: "96%" },
  { roll: "13", name: "Rohan Gupta", status: "absent", match: "—" },
  { roll: "14", name: "Saanvi Shah", status: "present", match: "92%" },
  { roll: "15", name: "Vihaan Das", status: "present", match: "90%" },
  { roll: "16", name: "Zoya Khan", status: "present", match: "95%" },
];

const statusContent = {
  present: { letter: "P", label: "Present" },
  absent: { letter: "A", label: "Absent" },
  review: { letter: "?", label: "Needs review" },
};

function Brand() {
  return (
    <button
      className="brand"
      onClick={() => window.scrollTo({ top: 0, behavior: "smooth" })}
      aria-label="AttendanceTrac home"
    >
      <span className="brand-mark">AT</span>
      <span>AttendanceTrac</span>
    </button>
  );
}

function Header({ onSignOut }: { onSignOut: () => void }) {
  return (
    <header className="topbar">
      <div className="page-width topbar-inner">
        <Brand />
        <div className="account">
          <span className="teacher-name">Neha Kulkarni</span>
          <span className="divider" />
          <button className="text-link" onClick={onSignOut}>
            Sign out
          </button>
        </div>
      </div>
    </header>
  );
}

function SignIn({ onSignIn }: { onSignIn: () => void }) {
  function submit(event: FormEvent) {
    event.preventDefault();
    onSignIn();
  }

  return (
    <main className="signin-page">
      <section className="signin-intro">
        <div>
          <Brand />
          <h1>Attendance, without the roll call.</h1>
          <p>Take attendance from a single photo of your class.</p>
        </div>
        <p className="school-note">Made for busy classrooms.</p>
      </section>

      <section className="signin-panel">
        <form className="signin-form" onSubmit={submit}>
          <div className="form-heading">
            <p className="eyebrow">Teacher portal</p>
            <h2>Welcome back</h2>
            <p>Sign in with your school-issued account.</p>
          </div>

          <label>
            <span>Email address</span>
            <input
              type="email"
              defaultValue="neha.kulkarni@vidyamandir.edu"
              required
            />
          </label>
          <label>
            <span>Password</span>
            <input type="password" defaultValue="attendance" required />
          </label>
          <button className="button primary full" type="submit">
            Sign in
          </button>
          <button className="forgot-link" type="button">
            Forgot password?
          </button>
        </form>
        <p className="security-note">Secure access for Vidya Mandir School</p>
      </section>
    </main>
  );
}

function Dashboard({
  onUpload,
  onView,
  onSignOut,
}: {
  onUpload: () => void;
  onView: () => void;
  onSignOut: () => void;
}) {
  const sessions = [
    ["18 Jul 2025", "Class 10-B", "14 / 16"],
    ["17 Jul 2025", "Class 10-B", "15 / 16"],
    ["16 Jul 2025", "Class 9-A", "28 / 30"],
    ["15 Jul 2025", "Class 10-B", "16 / 16"],
  ];

  return (
    <div className="app-page">
      <Header onSignOut={onSignOut} />
      <main className="page-width dashboard-main">
        <section className="dashboard-head">
          <p className="eyebrow">Friday, 18 July</p>
          <h1>Take attendance</h1>
          <p>Choose your class, then add one clear photo.</p>
        </section>

        <section className="capture-card">
          <div className="field-row">
            <label>
              <span>Class</span>
              <select defaultValue="10-B">
                <option>10-B</option>
                <option>9-A</option>
                <option>8-C</option>
              </select>
            </label>
            <label>
              <span>Date</span>
              <input type="date" defaultValue="2025-07-18" />
            </label>
          </div>
          <button className="upload-button" onClick={onUpload}>
            <span className="upload-symbol" aria-hidden="true">
              ↑
            </span>
            <span>
              <strong>Upload class photo</strong>
              <small>Choose from your device</small>
            </span>
          </button>
          <p className="upload-note">
            JPG or PNG, up to 10 MB. Everyone should be facing the camera.
          </p>
        </section>

        <section className="sessions-section">
          <div className="section-title">
            <div>
              <p className="eyebrow">Recent activity</p>
              <h2>Past sessions</h2>
            </div>
            <span>Last 30 days</span>
          </div>
          <div className="table-shell">
            <table>
              <thead>
                <tr>
                  <th>Date</th>
                  <th>Class</th>
                  <th>Present / total</th>
                  <th aria-label="Actions" />
                </tr>
              </thead>
              <tbody>
                {sessions.map(([date, className, count]) => (
                  <tr key={`${date}-${className}`}>
                    <td>{date}</td>
                    <td>{className}</td>
                    <td className="tabular">{count}</td>
                    <td>
                      <button className="view-link" onClick={onView}>
                        View
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </section>
      </main>
    </div>
  );
}

function Processing({
  onDone,
  onSignOut,
}: {
  onDone: () => void;
  onSignOut: () => void;
}) {
  const [progress, setProgress] = useState(18);

  useEffect(() => {
    const interval = window.setInterval(() => {
      setProgress((current) => Math.min(current + 7, 96));
    }, 180);
    const timeout = window.setTimeout(onDone, 2500);
    return () => {
      window.clearInterval(interval);
      window.clearTimeout(timeout);
    };
  }, [onDone]);

  return (
    <div className="app-page">
      <Header onSignOut={onSignOut} />
      <main className="page-width processing-main">
        <div className="processing-photo">
          <img src={classPhoto} alt="Uploaded class group" />
          <div className="scan-line" />
        </div>
        <section className="processing-copy" aria-live="polite">
          <p className="eyebrow">Analysing photo</p>
          <h1>Finding faces in your photo.</h1>
          <p>This can take up to a minute.</p>
          <div
            className="progress-track"
            role="progressbar"
            aria-valuemin={0}
            aria-valuemax={100}
            aria-valuenow={progress}
          >
            <span style={{ width: `${progress}%` }} />
          </div>
          <div className="progress-meta">
            <span>Matching with Class 10-B</span>
            <span>{progress}%</span>
          </div>
        </section>
      </main>
    </div>
  );
}

const faceBoxes = [
  ["1", "18%", "28%"],
  ["2", "38%", "24%"],
  ["3", "59%", "29%"],
  ["4", "76%", "20%"],
  ["5", "29%", "52%"],
  ["6", "51%", "49%"],
  ["7", "70%", "50%"],
  ["8", "44%", "70%"],
];

function Results({
  onAnother,
  onSignOut,
}: {
  onAnother: () => void;
  onSignOut: () => void;
}) {
  const [saved, setSaved] = useState(false);

  function downloadCsv() {
    const rows = [
      ["Roll no.", "Name", "Status", "Match"],
      ...students.map((student) => [
        student.roll,
        student.name,
        statusContent[student.status].label,
        student.match,
      ]),
    ];
    const csv = rows.map((row) => row.join(",")).join("\n");
    const href = URL.createObjectURL(new Blob([csv], { type: "text/csv" }));
    const link = document.createElement("a");
    link.href = href;
    link.download = "attendance-class-10-b.csv";
    link.click();
    URL.revokeObjectURL(href);
    setSaved(true);
  }

  return (
    <div className="app-page">
      <Header onSignOut={onSignOut} />
      <main className="page-width results-main">
        <div className="results-heading">
          <div>
            <p className="eyebrow">Class 10-B · 18 July 2025</p>
            <h1>Attendance results</h1>
          </div>
          <div className="summary-line" aria-label="Attendance summary">
            <span className="summary present">
              <b>11</b> Present
            </span>
            <span className="summary absent">
              <b>3</b> Absent
            </span>
            <span className="summary review">
              <b>2</b> Needs review
            </span>
          </div>
        </div>

        <div className="results-layout">
          <section className="table-shell attendance-table">
            <table>
              <thead>
                <tr>
                  <th>Roll no.</th>
                  <th>Name</th>
                  <th>Status</th>
                  <th>Match</th>
                  <th aria-label="Actions" />
                </tr>
              </thead>
              <tbody>
                {students.map((student) => {
                  const status = statusContent[student.status];
                  return (
                    <tr
                      key={student.roll}
                      className={student.status === "review" ? "needs-review" : ""}
                    >
                      <td className="tabular">{student.roll}</td>
                      <td className="student-name">{student.name}</td>
                      <td>
                        <span className={`status ${student.status}`}>
                          <b>{status.letter}</b>
                          {status.label}
                        </span>
                      </td>
                      <td className="match">{student.match}</td>
                      <td>
                        {student.status === "review" && (
                          <button
                            className="review-button"
                            onClick={() =>
                              document
                                .getElementById("face-review")
                                ?.scrollIntoView({ behavior: "smooth" })
                            }
                          >
                            Review
                          </button>
                        )}
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </section>

          <aside className="photo-panel">
            <div className="photo-heading">
              <h2>Uploaded photo</h2>
              <span>16 faces found</span>
            </div>
            <div className="tagged-photo">
              <img src={classPhoto} alt="Class photo with identified faces" />
              {faceBoxes.map(([number, left, top]) => (
                <span
                  className="face-box"
                  style={{ left, top }}
                  key={number}
                >
                  {number}
                </span>
              ))}
            </div>
            <p>Numbers correspond to detected faces in the photo.</p>
          </aside>
        </div>

        <section className="face-review" id="face-review">
          <div className="review-heading">
            <div>
              <p className="eyebrow">2 matches below confidence threshold</p>
              <h2>Faces that need review</h2>
            </div>
            <p>Confirm who each face belongs to before downloading.</p>
          </div>
          <div className="review-grid">
            <label className="face-card">
              <div className="face-crop face-one">
                <img src={classPhoto} alt="Unconfirmed face 1" />
                <span>Face 3</span>
              </div>
              <span>Match this face</span>
              <select defaultValue="Ananya Iyer">
                <option>Ananya Iyer</option>
                <option>Pranav Rao</option>
                <option>Not in this class</option>
              </select>
            </label>
            <label className="face-card">
              <div className="face-crop face-two">
                <img src={classPhoto} alt="Unconfirmed face 2" />
                <span>Face 7</span>
              </div>
              <span>Match this face</span>
              <select defaultValue="Pranav Rao">
                <option>Pranav Rao</option>
                <option>Ananya Iyer</option>
                <option>Not in this class</option>
              </select>
            </label>
          </div>
        </section>

        <footer className="result-actions">
          <p>{saved ? "Attendance file downloaded." : "Review complete? Save a copy for your records."}</p>
          <div>
            <button className="button secondary" onClick={onAnother}>
              Upload another photo
            </button>
            <button className="button primary" onClick={downloadCsv}>
              Download Excel
            </button>
          </div>
        </footer>
      </main>
    </div>
  );
}

export default function App() {
  const [screen, setScreen] = useState<Screen>("signin");

  if (screen === "signin") {
    return <SignIn onSignIn={() => setScreen("dashboard")} />;
  }
  if (screen === "dashboard") {
    return (
      <Dashboard
        onUpload={() => setScreen("processing")}
        onView={() => setScreen("results")}
        onSignOut={() => setScreen("signin")}
      />
    );
  }
  if (screen === "processing") {
    return (
      <Processing
        onDone={() => setScreen("results")}
        onSignOut={() => setScreen("signin")}
      />
    );
  }
  return (
    <Results
      onAnother={() => setScreen("dashboard")}
      onSignOut={() => setScreen("signin")}
    />
  );
}
