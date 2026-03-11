import { useState } from 'react';
import { Button, Card, Input, InputNumber, Typography, Badge, message, ConfigProvider } from 'antd';
import type { CSSProperties } from 'react';

export default function GeneratedApp() {
  const [messageApi, contextHolder] = message.useMessage();

  const [student1_name, setStudent1_name] = useState<string>('Student 1');
  const [student1_nepali, setStudent1_nepali] = useState<number>(0);
  const [student1_english, setStudent1_english] = useState<number>(0);
  const [student1_mathematics, setStudent1_mathematics] = useState<number>(0);
  const [student1_science, setStudent1_science] = useState<number>(0);
  const [student1_social_studies, setStudent1_social_studies] = useState<number>(0);
  const [student1_economics, setStudent1_economics] = useState<number>(0);
  const [student1_percentage, setStudent1_percentage] = useState<number>(0);
  const [student1_gpa, setStudent1_gpa] = useState<number>(0);
  const [student1_rank, setStudent1_rank] = useState<number>(0);
  const [student1_grade, setStudent1_grade] = useState<string>('');

  const [student2_name, setStudent2_name] = useState<string>('Student 2');
  const [student2_nepali, setStudent2_nepali] = useState<number>(0);
  const [student2_english, setStudent2_english] = useState<number>(0);
  const [student2_mathematics, setStudent2_mathematics] = useState<number>(0);
  const [student2_science, setStudent2_science] = useState<number>(0);
  const [student2_social_studies, setStudent2_social_studies] = useState<number>(0);
  const [student2_economics, setStudent2_economics] = useState<number>(0);
  const [student2_percentage, setStudent2_percentage] = useState<number>(0);
  const [student2_gpa, setStudent2_gpa] = useState<number>(0);
  const [student2_rank, setStudent2_rank] = useState<number>(0);
  const [student2_grade, setStudent2_grade] = useState<string>('');

  const [student3_name, setStudent3_name] = useState<string>('Student 3');
  const [student3_nepali, setStudent3_nepali] = useState<number>(0);
  const [student3_english, setStudent3_english] = useState<number>(0);
  const [student3_mathematics, setStudent3_mathematics] = useState<number>(0);
  const [student3_science, setStudent3_science] = useState<number>(0);
  const [student3_social_studies, setStudent3_social_studies] = useState<number>(0);
  const [student3_economics, setStudent3_economics] = useState<number>(0);
  const [student3_percentage, setStudent3_percentage] = useState<number>(0);
  const [student3_gpa, setStudent3_gpa] = useState<number>(0);
  const [student3_rank, setStudent3_rank] = useState<number>(0);
  const [student3_grade, setStudent3_grade] = useState<string>('');

  const [student4_name, setStudent4_name] = useState<string>('Student 4');
  const [student4_nepali, setStudent4_nepali] = useState<number>(0);
  const [student4_english, setStudent4_english] = useState<number>(0);
  const [student4_mathematics, setStudent4_mathematics] = useState<number>(0);
  const [student4_science, setStudent4_science] = useState<number>(0);
  const [student4_social_studies, setStudent4_social_studies] = useState<number>(0);
  const [student4_economics, setStudent4_economics] = useState<number>(0);
  const [student4_percentage, setStudent4_percentage] = useState<number>(0);
  const [student4_gpa, setStudent4_gpa] = useState<number>(0);
  const [student4_rank, setStudent4_rank] = useState<number>(0);
  const [student4_grade, setStudent4_grade] = useState<string>('');

  const handleCalculatePercentageGpa = () => {
    const s1_nepali = student1_nepali;
    const s1_english = student1_english;
    const s1_mathematics = student1_mathematics;
    const s1_science = student1_science;
    const s1_social_studies = student1_social_studies;
    const s1_economics = student1_economics;
    const s1_perc = (s1_nepali + s1_english + s1_mathematics + s1_science + s1_social_studies + s1_economics) / 6;
    const s1_gpa_val = s1_perc / 25;
    setStudent1_percentage(s1_perc);
    setStudent1_gpa(s1_gpa_val);

    const s2_nepali = student2_nepali;
    const s2_english = student2_english;
    const s2_mathematics = student2_mathematics;
    const s2_science = student2_science;
    const s2_social_studies = student2_social_studies;
    const s2_economics = student2_economics;
    const s2_perc = (s2_nepali + s2_english + s2_mathematics + s2_science + s2_social_studies + s2_economics) / 6;
    const s2_gpa_val = s2_perc / 25;
    setStudent2_percentage(s2_perc);
    setStudent2_gpa(s2_gpa_val);

    const s3_nepali = student3_nepali;
    const s3_english = student3_english;
    const s3_mathematics = student3_mathematics;
    const s3_science = student3_science;
    const s3_social_studies = student3_social_studies;
    const s3_economics = student3_economics;
    const s3_perc = (s3_nepali + s3_english + s3_mathematics + s3_science + s3_social_studies + s3_economics) / 6;
    const s3_gpa_val = s3_perc / 25;
    setStudent3_percentage(s3_perc);
    setStudent3_gpa(s3_gpa_val);

    const s4_nepali = student4_nepali;
    const s4_english = student4_english;
    const s4_mathematics = student4_mathematics;
    const s4_science = student4_science;
    const s4_social_studies = student4_social_studies;
    const s4_economics = student4_economics;
    const s4_perc = (s4_nepali + s4_english + s4_mathematics + s4_science + s4_social_studies + s4_economics) / 6;
    const s4_gpa_val = s4_perc / 25;
    setStudent4_percentage(s4_perc);
    setStudent4_gpa(s4_gpa_val);

    messageApi.success('Percentage and GPA calculated successfully');
  };

  const handleCalculateRankGrade = () => {
    const s1_perc = student1_percentage;
    const s2_perc = student2_percentage;
    const s3_perc = student3_percentage;
    const s4_perc = student4_percentage;

    const s1_rank_val = 1 + (s1_perc < s2_perc ? 1 : 0) + (s1_perc < s3_perc ? 1 : 0) + (s1_perc < s4_perc ? 1 : 0);
    const s1_grade_val = s1_perc >= 90 ? 'A+' : s1_perc >= 80 ? 'A' : s1_perc >= 70 ? 'B+' : s1_perc >= 60 ? 'B' : s1_perc >= 50 ? 'C+' : s1_perc >= 40 ? 'C' : 'F';
    setStudent1_rank(s1_rank_val);
    setStudent1_grade(s1_grade_val);

    const s2_rank_val = 1 + (s2_perc < s1_perc ? 1 : 0) + (s2_perc < s3_perc ? 1 : 0) + (s2_perc < s4_perc ? 1 : 0);
    const s2_grade_val = s2_perc >= 90 ? 'A+' : s2_perc >= 80 ? 'A' : s2_perc >= 70 ? 'B+' : s2_perc >= 60 ? 'B' : s2_perc >= 50 ? 'C+' : s2_perc >= 40 ? 'C' : 'F';
    setStudent2_rank(s2_rank_val);
    setStudent2_grade(s2_grade_val);

    const s3_rank_val = 1 + (s3_perc < s1_perc ? 1 : 0) + (s3_perc < s2_perc ? 1 : 0) + (s3_perc < s4_perc ? 1 : 0);
    const s3_grade_val = s3_perc >= 90 ? 'A+' : s3_perc >= 80 ? 'A' : s3_perc >= 70 ? 'B+' : s3_perc >= 60 ? 'B' : s3_perc >= 50 ? 'C+' : s3_perc >= 40 ? 'C' : 'F';
    setStudent3_rank(s3_rank_val);
    setStudent3_grade(s3_grade_val);

    const s4_rank_val = 1 + (s4_perc < s1_perc ? 1 : 0) + (s4_perc < s2_perc ? 1 : 0) + (s4_perc < s3_perc ? 1 : 0);
    const s4_grade_val = s4_perc >= 90 ? 'A+' : s4_perc >= 80 ? 'A' : s4_perc >= 70 ? 'B+' : s4_perc >= 60 ? 'B' : s4_perc >= 50 ? 'C+' : s4_perc >= 40 ? 'C' : 'F';
    setStudent4_rank(s4_rank_val);
    setStudent4_grade(s4_grade_val);

    messageApi.success('Rank and Grade calculated successfully');
  };

  const rootContainerStyle: CSSProperties = {
    height: '100vh',
    width: '100vw',
    padding: '32px',
    backgroundColor: '#0a0a0a',
    overflow: 'auto'
  };

  const titleStyle: CSSProperties = {
    textAlign: 'center',
    marginBottom: '32px',
    color: '#e0e0e0',
    fontFamily: 'Courier New, monospace',
    textTransform: 'uppercase',
    letterSpacing: '2px',
    fontWeight: 300
  };

  const cardStyle: CSSProperties = {
    marginBottom: '24px',
    backgroundColor: '#1a1a1a',
    border: '1px solid #333',
    borderRadius: '0'
  };

  const inputStyle: CSSProperties = {
    marginBottom: '16px',
    backgroundColor: '#0a0a0a',
    border: '1px solid #333',
    borderRadius: '0',
    color: '#e0e0e0'
  };

  const subjectsGridStyle: CSSProperties = {
    display: 'grid',
    gridTemplateColumns: '1fr 1fr',
    gap: '16px',
    marginBottom: '16px'
  };

  const inputNumberStyle: CSSProperties = {
    width: '100%',
    backgroundColor: '#0a0a0a',
    border: '1px solid #333',
    borderRadius: '0',
    color: '#e0e0e0'
  };

  const resultsStyle: CSSProperties = {
    marginTop: '20px',
    padding: '16px',
    backgroundColor: '#0a0a0a',
    border: '1px solid #333',
    borderRadius: '0'
  };

  const textStyle: CSSProperties = {
    display: 'block',
    marginBottom: '10px',
    color: '#e0e0e0',
    fontFamily: 'Courier New, monospace'
  };

  const buttonContainerStyle: CSSProperties = {
    display: 'flex',
    gap: '20px',
    justifyContent: 'center',
    marginTop: '32px'
  };

  const primaryButtonStyle: CSSProperties = {
    backgroundColor: '#1a1a1a',
    border: '1px solid #666',
    borderRadius: '0',
    color: '#e0e0e0',
    fontFamily: 'Courier New, monospace',
    textTransform: 'uppercase',
    letterSpacing: '1px'
  };

  const defaultButtonStyle: CSSProperties = {
    backgroundColor: '#0a0a0a',
    border: '1px solid #666',
    borderRadius: '0',
    color: '#e0e0e0',
    fontFamily: 'Courier New, monospace',
    textTransform: 'uppercase',
    letterSpacing: '1px'
  };

  return (
    <ConfigProvider
      theme={{
        token: {
          colorPrimary: '#1a1a1a',
          fontFamily: 'Courier New, monospace',
          borderRadius: 0
        }
      }}
    >
      {contextHolder}
      <div style={rootContainerStyle}>
        <Typography.Title level={2} style={titleStyle}>
          Student Marks Management System
        </Typography.Title>

        <Card title="Student 1" style={cardStyle}>
          <Input
            placeholder="Enter student name"
            value={student1_name}
            onChange={(e) => setStudent1_name(e.target.value)}
            style={inputStyle}
          />
          <div style={subjectsGridStyle}>
            <InputNumber
              min={0}
              max={100}
              placeholder="Nepali marks"
              value={student1_nepali}
              onChange={(val) => setStudent1_nepali(val ?? 0)}
              style={inputNumberStyle}
            />
            <InputNumber
              min={0}
              max={100}
              placeholder="English marks"
              value={student1_english}
              onChange={(val) => setStudent1_english(val ?? 0)}
              style={inputNumberStyle}
            />
            <InputNumber
              min={0}
              max={100}
              placeholder="Mathematics marks"
              value={student1_mathematics}
              onChange={(val) => setStudent1_mathematics(val ?? 0)}
              style={inputNumberStyle}
            />
            <InputNumber
              min={0}
              max={100}
              placeholder="Science marks"
              value={student1_science}
              onChange={(val) => setStudent1_science(val ?? 0)}
              style={inputNumberStyle}
            />
            <InputNumber
              min={0}
              max={100}
              placeholder="Social Studies marks"
              value={student1_social_studies}
              onChange={(val) => setStudent1_social_studies(val ?? 0)}
              style={inputNumberStyle}
            />
            <InputNumber
              min={0}
              max={100}
              placeholder="Economics marks"
              value={student1_economics}
              onChange={(val) => setStudent1_economics(val ?? 0)}
              style={inputNumberStyle}
            />
          </div>
          <div style={resultsStyle}>
            <Typography.Text strong style={textStyle}>
              Percentage: {student1_percentage.toFixed(2)}%
            </Typography.Text>
            <Typography.Text strong style={textStyle}>
              GPA: {student1_gpa.toFixed(2)}
            </Typography.Text>
            <Typography.Text strong style={textStyle}>
              Rank: {student1_rank}
            </Typography.Text>
            <Badge count={student1_grade} showZero style={{ backgroundColor: '#333', color: '#e0e0e0', border: '1px solid #666' }} />
          </div>
        </Card>

        <Card title="Student 2" style={cardStyle}>
          <Input
            placeholder="Enter student name"
            value={student2_name}
            onChange={(e) => setStudent2_name(e.target.value)}
            style={inputStyle}
          />
          <div style={subjectsGridStyle}>
            <InputNumber
              min={0}
              max={100}
              placeholder="Nepali marks"
              value={student2_nepali}
              onChange={(val) => setStudent2_nepali(val ?? 0)}
              style={inputNumberStyle}
            />
            <InputNumber
              min={0}
              max={100}
              placeholder="English marks"
              value={student2_english}
              onChange={(val) => setStudent2_english(val ?? 0)}
              style={inputNumberStyle}
            />
            <InputNumber
              min={0}
              max={100}
              placeholder="Mathematics marks"
              value={student2_mathematics}
              onChange={(val) => setStudent2_mathematics(val ?? 0)}
              style={inputNumberStyle}
            />
            <InputNumber
              min={0}
              max={100}
              placeholder="Science marks"
              value={student2_science}
              onChange={(val) => setStudent2_science(val ?? 0)}
              style={inputNumberStyle}
            />
            <InputNumber
              min={0}
              max={100}
              placeholder="Social Studies marks"
              value={student2_social_studies}
              onChange={(val) => setStudent2_social_studies(val ?? 0)}
              style={inputNumberStyle}
            />
            <InputNumber
              min={0}
              max={100}
              placeholder="Economics marks"
              value={student2_economics}
              onChange={(val) => setStudent2_economics(val ?? 0)}
              style={inputNumberStyle}
            />
          </div>
          <div style={resultsStyle}>
            <Typography.Text strong style={textStyle}>
              Percentage: {student2_percentage.toFixed(2)}%
            </Typography.Text>
            <Typography.Text strong style={textStyle}>
              GPA: {student2_gpa.toFixed(2)}
            </Typography.Text>
            <Typography.Text strong style={textStyle}>
              Rank: {student2_rank}
            </Typography.Text>
            <Badge count={student2_grade} showZero style={{ backgroundColor: '#333', color: '#e0e0e0', border: '1px solid #666' }} />
          </div>
        </Card>

        <Card title="Student 3" style={cardStyle}>
          <Input
            placeholder="Enter student name"
            value={student3_name}
            onChange={(e) => setStudent3_name(e.target.value)}
            style={inputStyle}
          />
          <div style={subjectsGridStyle}>
            <InputNumber
              min={0}
              max={100}
              placeholder="Nepali marks"
              value={student3_nepali}
              onChange={(val) => setStudent3_nepali(val ?? 0)}
              style={inputNumberStyle}
            />
            <InputNumber
              min={0}
              max={100}
              placeholder="English marks"
              value={student3_english}
              onChange={(val) => setStudent3_english(val ?? 0)}
              style={inputNumberStyle}
            />
            <InputNumber
              min={0}
              max={100}
              placeholder="Mathematics marks"
              value={student3_mathematics}
              onChange={(val) => setStudent3_mathematics(val ?? 0)}
              style={inputNumberStyle}
            />
            <InputNumber
              min={0}
              max={100}
              placeholder="Science marks"
              value={student3_science}
              onChange={(val) => setStudent3_science(val ?? 0)}
              style={inputNumberStyle}
            />
            <InputNumber
              min={0}
              max={100}
              placeholder="Social Studies marks"
              value={student3_social_studies}
              onChange={(val) => setStudent3_social_studies(val ?? 0)}
              style={inputNumberStyle}
            />
            <InputNumber
              min={0}
              max={100}
              placeholder="Economics marks"
              value={student3_economics}
              onChange={(val) => setStudent3_economics(val ?? 0)}
              style={inputNumberStyle}
            />
          </div>
          <div style={resultsStyle}>
            <Typography.Text strong style={textStyle}>
              Percentage: {student3_percentage.toFixed(2)}%
            </Typography.Text>
            <Typography.Text strong style={textStyle}>
              GPA: {student3_gpa.toFixed(2)}
            </Typography.Text>
            <Typography.Text strong style={textStyle}>
              Rank: {student3_rank}
            </Typography.Text>
            <Badge count={student3_grade} showZero style={{ backgroundColor: '#333', color: '#e0e0e0', border: '1px solid #666' }} />
          </div>
        </Card>

        <Card title="Student 4" style={cardStyle}>
          <Input
            placeholder="Enter student name"
            value={student4_name}
            onChange={(e) => setStudent4_name(e.target.value)}
            style={inputStyle}
          />
          <div style={subjectsGridStyle}>
            <InputNumber
              min={0}
              max={100}
              placeholder="Nepali marks"
              value={student4_nepali}
              onChange={(val) => setStudent4_nepali(val ?? 0)}
              style={inputNumberStyle}
            />
            <InputNumber
              min={0}
              max={100}
              placeholder="English marks"
              value={student4_english}
              onChange={(val) => setStudent4_english(val ?? 0)}
              style={inputNumberStyle}
            />
            <InputNumber
              min={0}
              max={100}
              placeholder="Mathematics marks"
              value={student4_mathematics}
              onChange={(val) => setStudent4_mathematics(val ?? 0)}
              style={inputNumberStyle}
            />
            <InputNumber
              min={0}
              max={100}
              placeholder="Science marks"
              value={student4_science}
              onChange={(val) => setStudent4_science(val ?? 0)}
              style={inputNumberStyle}
            />
            <InputNumber
              min={0}
              max={100}
              placeholder="Social Studies marks"
              value={student4_social_studies}
              onChange={(val) => setStudent4_social_studies(val ?? 0)}
              style={inputNumberStyle}
            />
            <InputNumber
              min={0}
              max={100}
              placeholder="Economics marks"
              value={student4_economics}
              onChange={(val) => setStudent4_economics(val ?? 0)}
              style={inputNumberStyle}
            />
          </div>
          <div style={resultsStyle}>
            <Typography.Text strong style={textStyle}>
              Percentage: {student4_percentage.toFixed(2)}%
            </Typography.Text>
            <Typography.Text strong style={textStyle}>
              GPA: {student4_gpa.toFixed(2)}
            </Typography.Text>
            <Typography.Text strong style={textStyle}>
              Rank: {student4_rank}
            </Typography.Text>
            <Badge count={student4_grade} showZero style={{ backgroundColor: '#333', color: '#e0e0e0', border: '1px solid #666' }} />
          </div>
        </Card>

        <div style={buttonContainerStyle}>
          <Button
            type="primary"
            size="large"
            onClick={handleCalculatePercentageGpa}
            style={primaryButtonStyle}
          >
            Calculate Percentage & GPA
          </Button>
          <Button
            type="default"
            size="large"
            onClick={handleCalculateRankGrade}
            style={defaultButtonStyle}
          >
            Calculate Rank & Grade
          </Button>
        </div>
      </div>
    </ConfigProvider>
  );
}
