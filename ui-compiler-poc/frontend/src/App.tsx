import { useState } from 'react';
import { ConfigProvider, theme, Card, Typography, InputNumber, Button, Badge, message } from 'antd';
import { CalculatorOutlined } from '@ant-design/icons';

const { Title, Text } = Typography;

export default function GeneratedApp() {
  const [messageApi, contextHolder] = message.useMessage();

  const [student1Name] = useState<string>('Aarav Sharma');
  const [student1Math, setStudent1Math] = useState<number | null>(null);
  const [student1Science, setStudent1Science] = useState<number | null>(null);
  const [student1English, setStudent1English] = useState<number | null>(null);
  const [student1Nepali, setStudent1Nepali] = useState<number | null>(null);
  const [student1Social, setStudent1Social] = useState<number | null>(null);
  const [student1Percentage, setStudent1Percentage] = useState<number | null>(null);
  const [student1Gpa, setStudent1Gpa] = useState<number | null>(null);
  const [student1Grade, setStudent1Grade] = useState<string | null>(null);

  const [student2Name] = useState<string>('Sita Thapa');
  const [student2Math, setStudent2Math] = useState<number | null>(null);
  const [student2Science, setStudent2Science] = useState<number | null>(null);
  const [student2English, setStudent2English] = useState<number | null>(null);
  const [student2Nepali, setStudent2Nepali] = useState<number | null>(null);
  const [student2Social, setStudent2Social] = useState<number | null>(null);
  const [student2Percentage, setStudent2Percentage] = useState<number | null>(null);
  const [student2Gpa, setStudent2Gpa] = useState<number | null>(null);
  const [student2Grade, setStudent2Grade] = useState<string | null>(null);

  const [student3Name] = useState<string>('Rajesh Gurung');
  const [student3Math, setStudent3Math] = useState<number | null>(null);
  const [student3Science, setStudent3Science] = useState<number | null>(null);
  const [student3English, setStudent3English] = useState<number | null>(null);
  const [student3Nepali, setStudent3Nepali] = useState<number | null>(null);
  const [student3Social, setStudent3Social] = useState<number | null>(null);
  const [student3Percentage, setStudent3Percentage] = useState<number | null>(null);
  const [student3Gpa, setStudent3Gpa] = useState<number | null>(null);
  const [student3Grade, setStudent3Grade] = useState<string | null>(null);

  const [student4Name] = useState<string>('Rijan Pokhrel');
  const [student4Math, setStudent4Math] = useState<number | null>(null);
  const [student4Science, setStudent4Science] = useState<number | null>(null);
  const [student4English, setStudent4English] = useState<number | null>(null);
  const [student4Nepali, setStudent4Nepali] = useState<number | null>(null);
  const [student4Social, setStudent4Social] = useState<number | null>(null);
  const [student4Percentage, setStudent4Percentage] = useState<number | null>(null);
  const [student4Gpa, setStudent4Gpa] = useState<number | null>(null);
  const [student4Grade, setStudent4Grade] = useState<string | null>(null);

  const calculateGrades = () => {
    if (
      student1Math === null || student1Science === null || student1English === null || student1Nepali === null || student1Social === null ||
      student2Math === null || student2Science === null || student2English === null || student2Nepali === null || student2Social === null ||
      student3Math === null || student3Science === null || student3English === null || student3Nepali === null || student3Social === null ||
      student4Math === null || student4Science === null || student4English === null || student4Nepali === null || student4Social === null
    ) {
      messageApi.error('Failed to calculate grades. Please check all marks are entered.');
      return;
    }

    const s1Avg = (student1Math + student1Science + student1English + student1Nepali + student1Social) / 5;
    setStudent1Percentage(s1Avg);
    setStudent1Gpa(s1Avg / 25);
    setStudent1Grade(
      s1Avg >= 90 ? 'A+' :
      s1Avg >= 80 ? 'A' :
      s1Avg >= 70 ? 'B+' :
      s1Avg >= 60 ? 'B' :
      s1Avg >= 50 ? 'C+' :
      s1Avg >= 40 ? 'C' : 'F'
    );

    const s2Avg = (student2Math + student2Science + student2English + student2Nepali + student2Social) / 5;
    setStudent2Percentage(s2Avg);
    setStudent2Gpa(s2Avg / 25);
    setStudent2Grade(
      s2Avg >= 90 ? 'A+' :
      s2Avg >= 80 ? 'A' :
      s2Avg >= 70 ? 'B+' :
      s2Avg >= 60 ? 'B' :
      s2Avg >= 50 ? 'C+' :
      s2Avg >= 40 ? 'C' : 'F'
    );

    const s3Avg = (student3Math + student3Science + student3English + student3Nepali + student3Social) / 5;
    setStudent3Percentage(s3Avg);
    setStudent3Gpa(s3Avg / 25);
    setStudent3Grade(
      s3Avg >= 90 ? 'A+' :
      s3Avg >= 80 ? 'A' :
      s3Avg >= 70 ? 'B+' :
      s3Avg >= 60 ? 'B' :
      s3Avg >= 50 ? 'C+' :
      s3Avg >= 40 ? 'C' : 'F'
    );

    const s4Avg = (student4Math + student4Science + student4English + student4Nepali + student4Social) / 5;
    setStudent4Percentage(s4Avg);
    setStudent4Gpa(s4Avg / 25);
    setStudent4Grade(
      s4Avg >= 90 ? 'A+' :
      s4Avg >= 80 ? 'A' :
      s4Avg >= 70 ? 'B+' :
      s4Avg >= 60 ? 'B' :
      s4Avg >= 50 ? 'C+' :
      s4Avg >= 40 ? 'C' : 'F'
    );

    messageApi.success('Grades calculated successfully!');
  };

  return (
    <ConfigProvider theme={{ token: { colorPrimary: '#1890ff', borderRadius: 8, fontFamily: 'Inter, -apple-system, BlinkMacSystemFont, \'Segoe UI\', Roboto, sans-serif' }, algorithm: theme.defaultAlgorithm }}>
      {contextHolder}
      <div style={{ minHeight: '100vh', height: '100%', width: '100%', display: 'flex', flexDirection: 'column', backgroundColor: '#f0f2f5' }}>
        <Card bordered={false} style={{ margin: '24px', textAlign: 'center', backgroundColor: '#ffffff', boxShadow: '0 2px 8px rgba(0,0,0,0.1)' }}>
          <Title level={1} style={{ marginBottom: '8px', color: '#1890ff' }}>Himalayan Secondary School</Title>
          <Text type="secondary" style={{ fontSize: '16px' }}>Kathmandu, Nepal</Text>
        </Card>

        <Card title="Student Marks Entry & Grade Calculation" bordered={false} style={{ margin: '0 24px 24px 24px', flex: 1, backgroundColor: '#ffffff', boxShadow: '0 2px 8px rgba(0,0,0,0.1)' }}>
          <div style={{ overflowX: 'auto' }}>
            <table style={{ width: '100%', borderCollapse: 'collapse' }}>
              <thead style={{ backgroundColor: '#fafafa' }}>
                <tr>
                  <th style={{ padding: '12px', textAlign: 'left', fontWeight: 600, borderBottom: '2px solid #f0f0f0' }}>Student Name</th>
                  <th style={{ padding: '12px', textAlign: 'center', fontWeight: 600, borderBottom: '2px solid #f0f0f0' }}>Mathematics</th>
                  <th style={{ padding: '12px', textAlign: 'center', fontWeight: 600, borderBottom: '2px solid #f0f0f0' }}>Science</th>
                  <th style={{ padding: '12px', textAlign: 'center', fontWeight: 600, borderBottom: '2px solid #f0f0f0' }}>English</th>
                  <th style={{ padding: '12px', textAlign: 'center', fontWeight: 600, borderBottom: '2px solid #f0f0f0' }}>Nepali</th>
                  <th style={{ padding: '12px', textAlign: 'center', fontWeight: 600, borderBottom: '2px solid #f0f0f0' }}>Social Studies</th>
                  <th style={{ padding: '12px', textAlign: 'center', fontWeight: 600, borderBottom: '2px solid #f0f0f0' }}>Percentage</th>
                  <th style={{ padding: '12px', textAlign: 'center', fontWeight: 600, borderBottom: '2px solid #f0f0f0' }}>GPA</th>
                  <th style={{ padding: '12px', textAlign: 'center', fontWeight: 600, borderBottom: '2px solid #f0f0f0' }}>Grade</th>
                </tr>
              </thead>
              <tbody>
                <tr>
                  <td style={{ padding: '12px', borderBottom: '1px solid #f0f0f0' }}>
                    <Text strong>{student1Name}</Text>
                  </td>
                  <td style={{ padding: '12px', borderBottom: '1px solid #f0f0f0' }}>
                    <InputNumber min={0} max={100} placeholder="0-100" style={{ width: '100%' }} value={student1Math} onChange={setStudent1Math} />
                  </td>
                  <td style={{ padding: '12px', borderBottom: '1px solid #f0f0f0' }}>
                    <InputNumber min={0} max={100} placeholder="0-100" style={{ width: '100%' }} value={student1Science} onChange={setStudent1Science} />
                  </td>
                  <td style={{ padding: '12px', borderBottom: '1px solid #f0f0f0' }}>
                    <InputNumber min={0} max={100} placeholder="0-100" style={{ width: '100%' }} value={student1English} onChange={setStudent1English} />
                  </td>
                  <td style={{ padding: '12px', borderBottom: '1px solid #f0f0f0' }}>
                    <InputNumber min={0} max={100} placeholder="0-100" style={{ width: '100%' }} value={student1Nepali} onChange={setStudent1Nepali} />
                  </td>
                  <td style={{ padding: '12px', borderBottom: '1px solid #f0f0f0' }}>
                    <InputNumber min={0} max={100} placeholder="0-100" style={{ width: '100%' }} value={student1Social} onChange={setStudent1Social} />
                  </td>
                  <td style={{ padding: '12px', textAlign: 'center', borderBottom: '1px solid #f0f0f0' }}>
                    <Text style={{ fontWeight: 500 }}>{student1Percentage !== null ? student1Percentage.toFixed(2) : ''}</Text>
                  </td>
                  <td style={{ padding: '12px', textAlign: 'center', borderBottom: '1px solid #f0f0f0' }}>
                    <Text style={{ fontWeight: 500 }}>{student1Gpa !== null ? student1Gpa.toFixed(2) : ''}</Text>
                  </td>
                  <td style={{ padding: '12px', textAlign: 'center', borderBottom: '1px solid #f0f0f0' }}>
                    <Badge status="success" text={student1Grade || ''} />
                  </td>
                </tr>

                <tr>
                  <td style={{ padding: '12px', borderBottom: '1px solid #f0f0f0' }}>
                    <Text strong>{student2Name}</Text>
                  </td>
                  <td style={{ padding: '12px', borderBottom: '1px solid #f0f0f0' }}>
                    <InputNumber min={0} max={100} placeholder="0-100" style={{ width: '100%' }} value={student2Math} onChange={setStudent2Math} />
                  </td>
                  <td style={{ padding: '12px', borderBottom: '1px solid #f0f0f0' }}>
                    <InputNumber min={0} max={100} placeholder="0-100" style={{ width: '100%' }} value={student2Science} onChange={setStudent2Science} />
                  </td>
                  <td style={{ padding: '12px', borderBottom: '1px solid #f0f0f0' }}>
                    <InputNumber min={0} max={100} placeholder="0-100" style={{ width: '100%' }} value={student2English} onChange={setStudent2English} />
                  </td>
                  <td style={{ padding: '12px', borderBottom: '1px solid #f0f0f0' }}>
                    <InputNumber min={0} max={100} placeholder="0-100" style={{ width: '100%' }} value={student2Nepali} onChange={setStudent2Nepali} />
                  </td>
                  <td style={{ padding: '12px', borderBottom: '1px solid #f0f0f0' }}>
                    <InputNumber min={0} max={100} placeholder="0-100" style={{ width: '100%' }} value={student2Social} onChange={setStudent2Social} />
                  </td>
                  <td style={{ padding: '12px', textAlign: 'center', borderBottom: '1px solid #f0f0f0' }}>
                    <Text style={{ fontWeight: 500 }}>{student2Percentage !== null ? student2Percentage.toFixed(2) : ''}</Text>
                  </td>
                  <td style={{ padding: '12px', textAlign: 'center', borderBottom: '1px solid #f0f0f0' }}>
                    <Text style={{ fontWeight: 500 }}>{student2Gpa !== null ? student2Gpa.toFixed(2) : ''}</Text>
                  </td>
                  <td style={{ padding: '12px', textAlign: 'center', borderBottom: '1px solid #f0f0f0' }}>
                    <Badge status="success" text={student2Grade || ''} />
                  </td>
                </tr>

                <tr>
                  <td style={{ padding: '12px', borderBottom: '1px solid #f0f0f0' }}>
                    <Text strong>{student3Name}</Text>
                  </td>
                  <td style={{ padding: '12px', borderBottom: '1px solid #f0f0f0' }}>
                    <InputNumber min={0} max={100} placeholder="0-100" style={{ width: '100%' }} value={student3Math} onChange={setStudent3Math} />
                  </td>
                  <td style={{ padding: '12px', borderBottom: '1px solid #f0f0f0' }}>
                    <InputNumber min={0} max={100} placeholder="0-100" style={{ width: '100%' }} value={student3Science} onChange={setStudent3Science} />
                  </td>
                  <td style={{ padding: '12px', borderBottom: '1px solid #f0f0f0' }}>
                    <InputNumber min={0} max={100} placeholder="0-100" style={{ width: '100%' }} value={student3English} onChange={setStudent3English} />
                  </td>
                  <td style={{ padding: '12px', borderBottom: '1px solid #f0f0f0' }}>
                    <InputNumber min={0} max={100} placeholder="0-100" style={{ width: '100%' }} value={student3Nepali} onChange={setStudent3Nepali} />
                  </td>
                  <td style={{ padding: '12px', borderBottom: '1px solid #f0f0f0' }}>
                    <InputNumber min={0} max={100} placeholder="0-100" style={{ width: '100%' }} value={student3Social} onChange={setStudent3Social} />
                  </td>
                  <td style={{ padding: '12px', textAlign: 'center', borderBottom: '1px solid #f0f0f0' }}>
                    <Text style={{ fontWeight: 500 }}>{student3Percentage !== null ? student3Percentage.toFixed(2) : ''}</Text>
                  </td>
                  <td style={{ padding: '12px', textAlign: 'center', borderBottom: '1px solid #f0f0f0' }}>
                    <Text style={{ fontWeight: 500 }}>{student3Gpa !== null ? student3Gpa.toFixed(2) : ''}</Text>
                  </td>
                  <td style={{ padding: '12px', textAlign: 'center', borderBottom: '1px solid #f0f0f0' }}>
                    <Badge status="success" text={student3Grade || ''} />
                  </td>
                </tr>

                <tr>
                  <td style={{ padding: '12px', borderBottom: '1px solid #f0f0f0' }}>
                    <Text strong>{student4Name}</Text>
                  </td>
                  <td style={{ padding: '12px', borderBottom: '1px solid #f0f0f0' }}>
                    <InputNumber min={0} max={100} placeholder="0-100" style={{ width: '100%' }} value={student4Math} onChange={setStudent4Math} />
                  </td>
                  <td style={{ padding: '12px', borderBottom: '1px solid #f0f0f0' }}>
                    <InputNumber min={0} max={100} placeholder="0-100" style={{ width: '100%' }} value={student4Science} onChange={setStudent4Science} />
                  </td>
                  <td style={{ padding: '12px', borderBottom: '1px solid #f0f0f0' }}>
                    <InputNumber min={0} max={100} placeholder="0-100" style={{ width: '100%' }} value={student4English} onChange={setStudent4English} />
                  </td>
                  <td style={{ padding: '12px', borderBottom: '1px solid #f0f0f0' }}>
                    <InputNumber min={0} max={100} placeholder="0-100" style={{ width: '100%' }} value={student4Nepali} onChange={setStudent4Nepali} />
                  </td>
                  <td style={{ padding: '12px', borderBottom: '1px solid #f0f0f0' }}>
                    <InputNumber min={0} max={100} placeholder="0-100" style={{ width: '100%' }} value={student4Social} onChange={setStudent4Social} />
                  </td>
                  <td style={{ padding: '12px', textAlign: 'center', borderBottom: '1px solid #f0f0f0' }}>
                    <Text style={{ fontWeight: 500 }}>{student4Percentage !== null ? student4Percentage.toFixed(2) : ''}</Text>
                  </td>
                  <td style={{ padding: '12px', textAlign: 'center', borderBottom: '1px solid #f0f0f0' }}>
                    <Text style={{ fontWeight: 500 }}>{student4Gpa !== null ? student4Gpa.toFixed(2) : ''}</Text>
                  </td>
                  <td style={{ padding: '12px', textAlign: 'center', borderBottom: '1px solid #f0f0f0' }}>
                    <Badge status="success" text={student4Grade || ''} />
                  </td>
                </tr>
              </tbody>
            </table>
          </div>

          <div style={{ display: 'flex', justifyContent: 'center', marginTop: '24px' }}>
            <Button type="primary" size="large" icon={<CalculatorOutlined />} onClick={calculateGrades}>
              Calculate Grades
            </Button>
          </div>
        </Card>
      </div>
    </ConfigProvider>
  );
}
