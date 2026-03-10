import { useState } from 'react';
import { Card, Typography, Button, InputNumber, message } from 'antd';
import { CalculatorOutlined } from '@ant-design/icons';
import type { CSSProperties } from 'react';

const { Title, Text } = Typography;

export default function GeneratedApp() {
  const [messageApi, contextHolder] = message.useMessage();

  const [student1_name] = useState<string>("Aarav Sharma");
  const [student1_nepali, setStudent1_nepali] = useState<number>(0);
  const [student1_english, setStudent1_english] = useState<number>(0);
  const [student1_mathematics, setStudent1_mathematics] = useState<number>(0);
  const [student1_science, setStudent1_science] = useState<number>(0);
  const [student1_social, setStudent1_social] = useState<number>(0);

  const [student2_name] = useState<string>("Sita Thapa");
  const [student2_nepali, setStudent2_nepali] = useState<number>(0);
  const [student2_english, setStudent2_english] = useState<number>(0);
  const [student2_mathematics, setStudent2_mathematics] = useState<number>(0);
  const [student2_science, setStudent2_science] = useState<number>(0);
  const [student2_social, setStudent2_social] = useState<number>(0);

  const [student3_name] = useState<string>("Rajesh Gurung");
  const [student3_nepali, setStudent3_nepali] = useState<number>(0);
  const [student3_english, setStudent3_english] = useState<number>(0);
  const [student3_mathematics, setStudent3_mathematics] = useState<number>(0);
  const [student3_science, setStudent3_science] = useState<number>(0);
  const [student3_social, setStudent3_social] = useState<number>(0);

  const [student1_percentage, setStudent1_percentage] = useState<number>(0);
  const [student1_gpa, setStudent1_gpa] = useState<number>(0);
  const [student1_grade, setStudent1_grade] = useState<string>("");

  const [student2_percentage, setStudent2_percentage] = useState<number>(0);
  const [student2_gpa, setStudent2_gpa] = useState<number>(0);
  const [student2_grade, setStudent2_grade] = useState<string>("");

  const [student3_percentage, setStudent3_percentage] = useState<number>(0);
  const [student3_gpa, setStudent3_gpa] = useState<number>(0);
  const [student3_grade, setStudent3_grade] = useState<string>("");

  const handleCalculate = () => {
    const s1_avg = (student1_nepali + student1_english + student1_mathematics + student1_science + student1_social) / 5;
    setStudent1_percentage(s1_avg);
    setStudent1_gpa(s1_avg / 25);
    setStudent1_grade(
      s1_avg >= 90 ? 'A+' :
      s1_avg >= 80 ? 'A' :
      s1_avg >= 70 ? 'B+' :
      s1_avg >= 60 ? 'B' :
      s1_avg >= 50 ? 'C+' :
      s1_avg >= 40 ? 'C' : 'F'
    );

    const s2_avg = (student2_nepali + student2_english + student2_mathematics + student2_science + student2_social) / 5;
    setStudent2_percentage(s2_avg);
    setStudent2_gpa(s2_avg / 25);
    setStudent2_grade(
      s2_avg >= 90 ? 'A+' :
      s2_avg >= 80 ? 'A' :
      s2_avg >= 70 ? 'B+' :
      s2_avg >= 60 ? 'B' :
      s2_avg >= 50 ? 'C+' :
      s2_avg >= 40 ? 'C' : 'F'
    );

    const s3_avg = (student3_nepali + student3_english + student3_mathematics + student3_science + student3_social) / 5;
    setStudent3_percentage(s3_avg);
    setStudent3_gpa(s3_avg / 25);
    setStudent3_grade(
      s3_avg >= 90 ? 'A+' :
      s3_avg >= 80 ? 'A' :
      s3_avg >= 70 ? 'B+' :
      s3_avg >= 60 ? 'B' :
      s3_avg >= 50 ? 'C+' :
      s3_avg >= 40 ? 'C' : 'F'
    );

    messageApi.success("Grades calculated successfully!");
  };

  const rootContainerStyle: CSSProperties = {
    minHeight: "100vh",
    backgroundColor: "#f0f2f5",
    padding: "24px"
  };

  const headerCardStyle: CSSProperties = {
    marginBottom: "24px",
    textAlign: "center",
    backgroundColor: "#ffffff"
  };

  const schoolNameStyle: CSSProperties = {
    color: "#1890ff",
    marginBottom: "8px"
  };

  const schoolAddressStyle: CSSProperties = {
    fontSize: "16px",
    color: "#595959"
  };

  const marksCardStyle: CSSProperties = {
    marginBottom: "24px"
  };

  const buttonContainerStyle: CSSProperties = {
    display: "flex",
    justifyContent: "flex-end",
    marginTop: "24px"
  };

  const tableContainerStyle: CSSProperties = {
    overflowX: "auto"
  };

  const tableStyle: CSSProperties = {
    width: "100%",
    borderCollapse: "collapse",
    border: "1px solid #f0f0f0"
  };

  const thStyle: CSSProperties = {
    backgroundColor: "#fafafa",
    padding: "12px 16px",
    textAlign: "left",
    fontWeight: 600,
    borderBottom: "1px solid #f0f0f0",
    borderRight: "1px solid #f0f0f0"
  };

  const tdStyle: CSSProperties = {
    padding: "12px 16px",
    borderBottom: "1px solid #f0f0f0",
    borderRight: "1px solid #f0f0f0"
  };

  return (
    <div style={rootContainerStyle}>
      {contextHolder}
      <Card bordered={true} style={headerCardStyle}>
        <Title level={2} style={schoolNameStyle}>Himalayan Secondary School</Title>
        <Text style={schoolAddressStyle}>Kathmandu, Nepal | Est. 1985</Text>
      </Card>

      <Card title="Student Marks Entry" bordered={true} style={marksCardStyle}>
        <div style={tableContainerStyle}>
          <table style={tableStyle}>
            <thead>
              <tr>
                <th style={thStyle}>Student Name</th>
                <th style={thStyle}>Nepali</th>
                <th style={thStyle}>English</th>
                <th style={thStyle}>Mathematics</th>
                <th style={thStyle}>Science</th>
                <th style={thStyle}>Social Studies</th>
                <th style={thStyle}>Percentage</th>
                <th style={thStyle}>GPA</th>
                <th style={thStyle}>Grade</th>
              </tr>
            </thead>
            <tbody>
              <tr>
                <td style={tdStyle}>{student1_name}</td>
                <td style={tdStyle}>
                  <InputNumber
                    min={0}
                    max={100}
                    value={student1_nepali}
                    onChange={(val) => setStudent1_nepali(val ?? 0)}
                    style={{ width: '100%' }}
                  />
                </td>
                <td style={tdStyle}>
                  <InputNumber
                    min={0}
                    max={100}
                    value={student1_english}
                    onChange={(val) => setStudent1_english(val ?? 0)}
                    style={{ width: '100%' }}
                  />
                </td>
                <td style={tdStyle}>
                  <InputNumber
                    min={0}
                    max={100}
                    value={student1_mathematics}
                    onChange={(val) => setStudent1_mathematics(val ?? 0)}
                    style={{ width: '100%' }}
                  />
                </td>
                <td style={tdStyle}>
                  <InputNumber
                    min={0}
                    max={100}
                    value={student1_science}
                    onChange={(val) => setStudent1_science(val ?? 0)}
                    style={{ width: '100%' }}
                  />
                </td>
                <td style={tdStyle}>
                  <InputNumber
                    min={0}
                    max={100}
                    value={student1_social}
                    onChange={(val) => setStudent1_social(val ?? 0)}
                    style={{ width: '100%' }}
                  />
                </td>
                <td style={tdStyle}>{student1_percentage.toFixed(2)}</td>
                <td style={tdStyle}>{student1_gpa.toFixed(2)}</td>
                <td style={tdStyle}>{student1_grade}</td>
              </tr>
              <tr>
                <td style={tdStyle}>{student2_name}</td>
                <td style={tdStyle}>
                  <InputNumber
                    min={0}
                    max={100}
                    value={student2_nepali}
                    onChange={(val) => setStudent2_nepali(val ?? 0)}
                    style={{ width: '100%' }}
                  />
                </td>
                <td style={tdStyle}>
                  <InputNumber
                    min={0}
                    max={100}
                    value={student2_english}
                    onChange={(val) => setStudent2_english(val ?? 0)}
                    style={{ width: '100%' }}
                  />
                </td>
                <td style={tdStyle}>
                  <InputNumber
                    min={0}
                    max={100}
                    value={student2_mathematics}
                    onChange={(val) => setStudent2_mathematics(val ?? 0)}
                    style={{ width: '100%' }}
                  />
                </td>
                <td style={tdStyle}>
                  <InputNumber
                    min={0}
                    max={100}
                    value={student2_science}
                    onChange={(val) => setStudent2_science(val ?? 0)}
                    style={{ width: '100%' }}
                  />
                </td>
                <td style={tdStyle}>
                  <InputNumber
                    min={0}
                    max={100}
                    value={student2_social}
                    onChange={(val) => setStudent2_social(val ?? 0)}
                    style={{ width: '100%' }}
                  />
                </td>
                <td style={tdStyle}>{student2_percentage.toFixed(2)}</td>
                <td style={tdStyle}>{student2_gpa.toFixed(2)}</td>
                <td style={tdStyle}>{student2_grade}</td>
              </tr>
              <tr>
                <td style={tdStyle}>{student3_name}</td>
                <td style={tdStyle}>
                  <InputNumber
                    min={0}
                    max={100}
                    value={student3_nepali}
                    onChange={(val) => setStudent3_nepali(val ?? 0)}
                    style={{ width: '100%' }}
                  />
                </td>
                <td style={tdStyle}>
                  <InputNumber
                    min={0}
                    max={100}
                    value={student3_english}
                    onChange={(val) => setStudent3_english(val ?? 0)}
                    style={{ width: '100%' }}
                  />
                </td>
                <td style={tdStyle}>
                  <InputNumber
                    min={0}
                    max={100}
                    value={student3_mathematics}
                    onChange={(val) => setStudent3_mathematics(val ?? 0)}
                    style={{ width: '100%' }}
                  />
                </td>
                <td style={tdStyle}>
                  <InputNumber
                    min={0}
                    max={100}
                    value={student3_science}
                    onChange={(val) => setStudent3_science(val ?? 0)}
                    style={{ width: '100%' }}
                  />
                </td>
                <td style={tdStyle}>
                  <InputNumber
                    min={0}
                    max={100}
                    value={student3_social}
                    onChange={(val) => setStudent3_social(val ?? 0)}
                    style={{ width: '100%' }}
                  />
                </td>
                <td style={tdStyle}>{student3_percentage.toFixed(2)}</td>
                <td style={tdStyle}>{student3_gpa.toFixed(2)}</td>
                <td style={tdStyle}>{student3_grade}</td>
              </tr>
            </tbody>
          </table>
        </div>
      </Card>

      <div style={buttonContainerStyle}>
        <Button
          type="primary"
          size="large"
          icon={<CalculatorOutlined />}
          onClick={handleCalculate}
        >
          Calculate Results
        </Button>
      </div>
    </div>
  );
}
