import { useEffect, useState, useMemo } from 'react';
import { Table, Button, Modal, Typography, Descriptions, Alert, message } from 'antd';
import { CalculatorOutlined } from '@ant-design/icons';
import type { TablePaginationConfig } from 'antd';
import initSqlJs from 'sql.js';
import type { Database } from 'sql.js';
import type { CSSProperties } from 'react';

interface Student {
  id: number;
  name: string;
  height: number;
  weight: number;
  bmi?: string;
  category?: string;
}

export default function GeneratedApp() {
  const [messageApi, contextHolder] = message.useMessage();
  const [rows, setRows] = useState<Student[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [page, setPage] = useState(1);
  const [pageSize, setPageSize] = useState(50);
  const [total, setTotal] = useState(0);
  const [selectedStudent, setSelectedStudent] = useState<Student | null>(null);
  const [modalVisible, setModalVisible] = useState(false);
  const [bmiCalculated, setBmiCalculated] = useState(false);
  const [db, setDb] = useState<Database | null>(null);

  useEffect(() => {
    const initDb = async () => {
      try {
        const SQL = await initSqlJs({ locateFile: () => '/db/sql-wasm.wasm' });
        const response = await fetch('/db/student_data.db');
        const buffer = await response.arrayBuffer();
        const database = new SQL.Database(new Uint8Array(buffer));
        setDb(database);
      } catch (err) {
        setError(`Failed to initialize database: ${err}`);
      }
    };
    initDb();
  }, []);

  useEffect(() => {
    if (!db) return;

    const fetchData = async () => {
      setLoading(true);
      setError('');
      try {
        const currentPage = Number(page);
        const currentPageSize = Number(pageSize);
        
        const safePage = Number.isInteger(currentPage) && currentPage > 0 ? currentPage : 1;
        const safePageSize = Number.isInteger(currentPageSize) && currentPageSize > 0 ? currentPageSize : 50;
        
        const offset = (safePage - 1) * safePageSize;
        const limit = safePageSize;

        const countQuery = "SELECT COUNT(*) as count FROM student_data WHERE ('' = '' OR name LIKE '%' || '' || '%')";
        const countResult = db.exec(countQuery);
        const totalCount = countResult.length > 0 ? (countResult[0].values[0][0] as number) : 0;
        setTotal(totalCount);

        const dataQuery = `SELECT id, name, height, weight FROM student_data WHERE ('' = '' OR name LIKE '%' || '' || '%') ORDER BY name LIMIT ${limit} OFFSET ${offset}`;
        const result = db.exec(dataQuery);

        if (result.length > 0) {
          const students: Student[] = result[0].values.map((row) => ({
            id: row[0] as number,
            name: row[1] as string,
            height: row[2] as number,
            weight: row[3] as number,
          }));
          setRows(students);
        } else {
          setRows([]);
        }
      } catch (err) {
        setError(`Query failed: ${err}`);
        setRows([]);
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, [db, page, pageSize]);

  const studentsWithBMI = useMemo(() => {
    if (bmiCalculated) {
      return rows.map((s) => {
        const bmiValue = s.weight / ((s.height / 100) * (s.height / 100));
        const bmi = bmiValue.toFixed(2);
        const category = bmiValue < 18.5 ? 'Underweight' : bmiValue > 25 ? 'Overweight' : 'Normal';
        return { ...s, bmi, category };
      });
    }
    return rows;
  }, [bmiCalculated, rows]);

  const calculateBMI = () => {
    setBmiCalculated(true);
    messageApi.success('BMI calculated successfully');
  };

  const openStudentModal = (student: Student) => {
    setSelectedStudent(student);
    setModalVisible(true);
  };

  const closeModal = () => {
    setModalVisible(false);
    setSelectedStudent(null);
  };

  const handleTableChange = (pagination: TablePaginationConfig) => {
    const newPage = pagination.current ?? 1;
    const newPageSize = pagination.pageSize ?? 50;
    setPage(newPage);
    setPageSize(newPageSize);
  };

  const columns = [
    {
      title: 'Name',
      dataIndex: 'name',
      key: 'name',
      width: '30%',
    },
    {
      title: 'Height (cm)',
      dataIndex: 'height',
      key: 'height',
      width: '20%',
    },
    {
      title: 'Weight (kg)',
      dataIndex: 'weight',
      key: 'weight',
      width: '20%',
    },
    {
      title: 'BMI',
      dataIndex: 'bmi',
      key: 'bmi',
      width: '15%',
      render: (text: string) => (bmiCalculated ? text : '-'),
    },
    {
      title: 'Category',
      dataIndex: 'category',
      key: 'category',
      width: '15%',
      render: (text: string) => (bmiCalculated ? text : '-'),
    },
  ];

  const rootContainerStyle: CSSProperties = {
    width: '100vw',
    height: '100vh',
    padding: '24px',
    backgroundColor: '#f5f5f5',
    overflow: 'auto',
  };

  const pageTitleStyle: CSSProperties = {
    marginBottom: '24px',
    textAlign: 'center',
  };

  const tableStyle: CSSProperties = {
    backgroundColor: '#ffffff',
    borderRadius: '8px',
    cursor: 'pointer',
  };

  const calculateButtonStyle: CSSProperties = {
    backgroundColor: '#52c41a',
    borderColor: '#52c41a',
    position: 'fixed',
    bottom: '24px',
    right: '24px',
    zIndex: 1000,
    boxShadow: '0 4px 12px rgba(0,0,0,0.15)',
  };

  const modalContentStyle: CSSProperties = {
    padding: '16px',
  };

  const modalNameStyle: CSSProperties = {
    marginBottom: '16px',
  };

  const modalCategoryAlertStyle: CSSProperties = {
    marginTop: '16px',
  };

  const getCategoryMessage = () => {
    if (!selectedStudent?.category) return 'Not calculated';
    if (selectedStudent.category === 'Underweight') return 'This student is underweight';
    if (selectedStudent.category === 'Overweight') return 'This student is overweight';
    return 'This student has normal weight';
  };

  const getCategoryType = () => {
    if (selectedStudent?.category === 'Normal') return 'success';
    return 'warning';
  };

  const descriptionsItems = [
    {
      label: 'Height',
      children: selectedStudent ? `${selectedStudent.height} cm` : '',
    },
    {
      label: 'Weight',
      children: selectedStudent ? `${selectedStudent.weight} kg` : '',
    },
    {
      label: 'BMI',
      children: selectedStudent?.bmi || 'Not calculated',
    },
    {
      label: 'Category',
      children: selectedStudent?.category || 'Not calculated',
    },
  ];

  return (
    <div style={rootContainerStyle}>
      {contextHolder}
      <Typography.Title level={2} style={pageTitleStyle}>
        Student BMI Dashboard
      </Typography.Title>
      {error && (
        <Alert
          message="Error"
          description={error}
          type="error"
          showIcon
          style={{ marginBottom: '24px' }}
        />
      )}
      <Table
        columns={columns}
        dataSource={studentsWithBMI}
        rowKey="id"
        pagination={{
          current: page,
          pageSize: pageSize,
          total: total,
          showSizeChanger: true,
        }}
        loading={loading}
        onRow={(record) => ({
          onClick: () => openStudentModal(record),
        })}
        onChange={handleTableChange}
        style={tableStyle}
      />
      <Button
        type="primary"
        size="large"
        icon={<CalculatorOutlined />}
        onClick={calculateBMI}
        style={calculateButtonStyle}
      >
        Calculate BMI
      </Button>
      <Modal
        open={modalVisible}
        onCancel={closeModal}
        title="Student BMI Details"
        footer={null}
        width={500}
      >
        <div style={modalContentStyle}>
          <Typography.Title level={4} style={modalNameStyle}>
            {selectedStudent?.name}
          </Typography.Title>
          <Descriptions column={1} bordered items={descriptionsItems} />
          {selectedStudent?.category && (
            <Alert
              message={getCategoryMessage()}
              type={getCategoryType()}
              showIcon
              style={modalCategoryAlertStyle}
            />
          )}
        </div>
      </Modal>
    </div>
  );
}
