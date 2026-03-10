import { useState, useEffect, useMemo } from 'react';
import { Table, Input, Button, Card, Typography, InputNumber, message } from 'antd';
import { ReloadOutlined } from '@ant-design/icons';
import type { TablePaginationConfig } from 'antd';
import initSqlJs from 'sql.js';
import type { Database } from 'sql.js';

interface StudentRow {
  id: number;
  name: string;
  height: number;
  weight: number;
  bmi: number;
  category: string;
}

export default function GeneratedApp() {
  const [messageApi, contextHolder] = message.useMessage();
  const [rows, setRows] = useState<StudentRow[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [page, setPage] = useState(1);
  const [pageSize, setPageSize] = useState(50);
  const [total, setTotal] = useState(0);
  const [search, setSearch] = useState('');
  const [manualHeight, setManualHeight] = useState(0);
  const [manualWeight, setManualWeight] = useState(0);
  const [calculatedBMI, setCalculatedBMI] = useState(0);
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
        const errMsg = err instanceof Error ? err.message : 'Failed to initialize database';
        setError(errMsg);
        messageApi.error(errMsg);
      }
    };
    initDb();
  }, [messageApi]);

  const loadStudents = async () => {
    if (!db) {
      const errMsg = 'Database not initialized';
      setError(errMsg);
      messageApi.error(errMsg);
      return;
    }

    setLoading(true);
    setError('');

    try {
      const currentPage = Number(page);
      const currentPageSize = Number(pageSize);
      const safePageNum = Number.isInteger(currentPage) && currentPage > 0 ? currentPage : 1;
      const safePageSizeNum = Number.isInteger(currentPageSize) && currentPageSize > 0 ? currentPageSize : 50;
      const offsetValue = (safePageNum - 1) * safePageSizeNum;

      const countSql = `SELECT COUNT(*) as count FROM student_data WHERE (:search = '' OR name LIKE '%' || :search || '%')`;
      const countResult = db.exec(countSql, { ':search': search });
      const totalCount = countResult.length > 0 && countResult[0].values.length > 0 
        ? Number(countResult[0].values[0][0]) 
        : 0;

      const dataSql = `SELECT id, name, height, weight FROM student_data WHERE (:search = '' OR name LIKE '%' || :search || '%') ORDER BY name LIMIT ${safePageSizeNum} OFFSET ${offsetValue}`;
      const result = db.exec(dataSql, { ':search': search });

      if (result.length > 0) {
        const data: StudentRow[] = result[0].values.map((row) => {
          const id = Number(row[0]);
          const name = String(row[1]);
          const height = Number(row[2]);
          const weight = Number(row[3]);
          const bmi = height > 0 ? weight / Math.pow(height / 100, 2) : 0;
          let category = '';
          if (bmi > 0) {
            if (bmi < 18.5) category = 'Underweight';
            else if (bmi < 25) category = 'Normal';
            else if (bmi < 30) category = 'Overweight';
            else category = 'Obese';
          }
          return { id, name, height, weight, bmi: Math.round(bmi * 10) / 10, category };
        });
        setRows(data);
      } else {
        setRows([]);
      }

      setTotal(totalCount);
      messageApi.success('Student data loaded successfully');
    } catch (err) {
      const errMsg = err instanceof Error ? err.message : 'Failed to load student data';
      setError(errMsg);
      messageApi.error(errMsg);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (db) {
      loadStudents();
    }
  }, [db, page, pageSize, search]);

  const tableData = useMemo(() => rows, [rows]);

  const handleSearchChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setSearch(e.target.value);
    setPage(1);
  };

  const handlePageChange = (pagination: TablePaginationConfig) => {
    setPage(pagination.current || 1);
    setPageSize(pagination.pageSize || 50);
  };

  const handleCalculateManualBMI = () => {
    const height = manualHeight;
    const weight = manualWeight;
    if (height > 0 && weight > 0) {
      const bmi = weight / Math.pow(height / 100, 2);
      setCalculatedBMI(Math.round(bmi * 10) / 10);
    } else {
      setCalculatedBMI(0);
    }
  };

  const columns = [
    {
      title: 'ID',
      dataIndex: 'id',
      key: 'id',
      width: 80,
    },
    {
      title: 'Name',
      dataIndex: 'name',
      key: 'name',
      width: 200,
    },
    {
      title: 'Height (cm)',
      dataIndex: 'height',
      key: 'height',
      width: 120,
    },
    {
      title: 'Weight (kg)',
      dataIndex: 'weight',
      key: 'weight',
      width: 120,
    },
    {
      title: 'BMI',
      dataIndex: 'bmi',
      key: 'bmi',
      width: 100,
    },
    {
      title: 'Category',
      dataIndex: 'category',
      key: 'category',
      width: 150,
    },
  ];

  return (
    <>
      {contextHolder}
      <div
        style={{
          padding: '24px',
          maxWidth: '1400px',
          margin: '0 auto',
          backgroundColor: '#1a1a1a',
          minHeight: '100vh',
          fontFamily: "'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif",
          height: '100vh',
          width: '100vw',
          overflow: 'auto',
          boxSizing: 'border-box',
        }}
      >
        <Typography.Title
          level={1}
          style={{
            marginBottom: '32px',
            color: '#f5f5f5',
            fontSize: '42px',
            fontWeight: '900',
            textTransform: 'uppercase',
            letterSpacing: '2px',
            textShadow: '3px 3px 0px #ff6b6b, 6px 6px 0px rgba(0,0,0,0.3)',
            position: 'relative',
          }}
        >
          Student BMI Calculator
        </Typography.Title>

        <Card
          size="small"
          bordered={false}
          style={{
            marginBottom: '32px',
            backgroundColor: '#2d2d2d',
            border: '3px solid #ff6b6b',
            borderRadius: '0px',
            boxShadow: '8px 8px 0px rgba(255, 107, 107, 0.3)',
          }}
        >
          <Typography.Text
            style={{
              color: '#e0e0e0',
              fontSize: '15px',
              lineHeight: '1.6',
              fontWeight: '500',
            }}
          >
            BMI is calculated as: weight (kg) / (height (m))². Height is stored in cm and converted automatically.
          </Typography.Text>
        </Card>

        <Card title="Manual BMI Calculator" style={{ marginBottom: '24px' }}>
          <div style={{ display: 'flex', gap: '16px', alignItems: 'flex-end' }}>
            <Typography.Text strong>Height (cm):</Typography.Text>
            <InputNumber
              placeholder="Height (cm)"
              min={0}
              max={300}
              style={{ width: '150px' }}
              variant="outlined"
              value={manualHeight}
              onChange={(value) => setManualHeight(value || 0)}
            />
            <Typography.Text strong>Weight (kg):</Typography.Text>
            <InputNumber
              placeholder="Weight (kg)"
              min={0}
              max={500}
              style={{ width: '150px' }}
              variant="outlined"
              value={manualWeight}
              onChange={(value) => setManualWeight(value || 0)}
            />
            <Button type="primary" onClick={handleCalculateManualBMI}>
              Calculate BMI
            </Button>
            <Typography.Text strong style={{ fontSize: '16px', marginLeft: '16px' }}>
              {calculatedBMI > 0 ? `BMI: ${calculatedBMI}` : ''}
            </Typography.Text>
          </div>
        </Card>

        <div
          style={{
            display: 'flex',
            gap: '16px',
            marginBottom: '32px',
            alignItems: 'center',
            flexWrap: 'wrap',
          }}
        >
          <Input.Search
            placeholder="Search students..."
            allowClear
            size="large"
            value={search}
            onChange={handleSearchChange}
            style={{
              width: '320px',
              backgroundColor: '#2d2d2d',
              border: '2px solid #4a4a4a',
              borderRadius: '0px',
              color: '#f5f5f5',
            }}
          />
          <Button
            type="primary"
            icon={<ReloadOutlined />}
            loading={loading}
            size="large"
            onClick={loadStudents}
            style={{
              backgroundColor: '#ff6b6b',
              border: 'none',
              borderRadius: '0px',
              fontWeight: '700',
              textTransform: 'uppercase',
              letterSpacing: '1px',
              boxShadow: '4px 4px 0px rgba(0, 0, 0, 0.4)',
              height: '44px',
              padding: '0 32px',
            }}
          >
            Refresh
          </Button>
        </div>

        {error && (
          <Typography.Text type="danger" style={{ display: 'block', marginBottom: '16px' }}>
            Error: {error}
          </Typography.Text>
        )}

        <Table
          columns={columns}
          dataSource={tableData}
          loading={loading}
          rowKey="id"
          bordered
          size="middle"
          onChange={handlePageChange}
          pagination={{
            current: page,
            pageSize: pageSize,
            total: total,
            showSizeChanger: true,
            showTotal: (total) => `Total ${total} items`,
          }}
          style={{
            backgroundColor: '#2d2d2d',
            border: '3px solid #4a4a4a',
            borderRadius: '0px',
            boxShadow: '10px 10px 0px rgba(0, 0, 0, 0.3)',
          }}
        />
      </div>
    </>
  );
}
