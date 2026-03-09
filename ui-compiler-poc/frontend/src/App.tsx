import { useEffect, useState } from 'react';
import { Button, Card, Input, InputNumber, Table, Typography, message } from 'antd';
import type { TablePaginationConfig } from 'antd';
import initSqlJs from 'sql.js';
import type { Database } from 'sql.js';

interface StudentRow {
  id: number;
  name: string;
  height: number;
  weight: number;
}

export default function GeneratedApp() {
  const [rows, setRows] = useState<StudentRow[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [page, setPage] = useState(1);
  const [pageSize, setPageSize] = useState(50);
  const [total, setTotal] = useState(0);
  const [newStudentName, setNewStudentName] = useState('');
  const [newStudentHeight, setNewStudentHeight] = useState<number | null>(null);
  const [newStudentWeight, setNewStudentWeight] = useState<number | null>(null);
  const [searchTerm, setSearchTerm] = useState('');
  const [db, setDb] = useState<Database | null>(null);
  const [messageApi, contextHolder] = message.useMessage();

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

  useEffect(() => {
    if (!db) return;

    const loadStudents = async () => {
      setLoading(true);
      setError('');

      try {
        const currentPage = Number(page);
        const currentPageSize = Number(pageSize);
        const safePage = Number.isInteger(currentPage) && currentPage > 0 ? currentPage : 1;
        const safePageSize = Number.isInteger(currentPageSize) && currentPageSize > 0 ? currentPageSize : 50;
        const offset = (safePage - 1) * safePageSize;

        const countSql = `SELECT COUNT(*) as count FROM student_data sd WHERE (:search = '' OR sd.name LIKE '%' || :search || '%')`;
        const countResult = db.exec(countSql, { ':search': searchTerm });
        const totalCount = countResult.length > 0 && countResult[0].values.length > 0 
          ? Number(countResult[0].values[0][0]) 
          : 0;
        setTotal(totalCount);

        const dataSql = `SELECT sd.id, sd.name, sd.height, sd.weight FROM student_data sd WHERE (:search = '' OR sd.name LIKE '%' || :search || '%') ORDER BY sd.id DESC LIMIT ${safePageSize} OFFSET ${offset}`;
        const dataResult = db.exec(dataSql, { ':search': searchTerm });

        if (dataResult.length > 0) {
          const mappedRows: StudentRow[] = dataResult[0].values.map((row) => ({
            id: Number(row[0]),
            name: String(row[1]),
            height: Number(row[2]),
            weight: Number(row[3]),
          }));
          setRows(mappedRows);
        } else {
          setRows([]);
        }
      } catch (err) {
        const errMsg = err instanceof Error ? err.message : 'Failed to load students';
        setError(errMsg);
        messageApi.error(errMsg);
      } finally {
        setLoading(false);
      }
    };

    loadStudents();
  }, [db, page, pageSize, searchTerm, messageApi]);

  const handleAddStudent = async () => {
    const name = newStudentName;
    const height = newStudentHeight;
    const weight = newStudentWeight;

    if (name === '' || height === null || height <= 0 || weight === null || weight <= 0) {
      messageApi.error('Failed to add student. Please check all fields.');
      return;
    }

    if (!db) {
      messageApi.error('Database not initialized');
      return;
    }

    try {
      db.run('INSERT INTO student_data (name, height, weight) VALUES (?, ?, ?)', [name, height, weight]);
      messageApi.success('Student added successfully');
      setNewStudentName('');
      setNewStudentHeight(null);
      setNewStudentWeight(null);
      setPage(1);
    } catch (err) {
      const errMsg = err instanceof Error ? err.message : 'Failed to add student';
      messageApi.error(errMsg);
    }
  };

  const handleTableChange = (pagination: TablePaginationConfig) => {
    if (pagination.current !== undefined) {
      setPage(pagination.current);
    }
    if (pagination.pageSize !== undefined) {
      setPageSize(pagination.pageSize);
      setPage(1);
    }
  };

  const handleSearchChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setSearchTerm(e.target.value);
    setPage(1);
  };

  return (
    <>
      {contextHolder}
      <div style={{ padding: '24px', maxWidth: '1200px', margin: '0 auto' }}>
        <Typography.Title level={2} style={{ marginBottom: '24px' }}>
          Student Management
        </Typography.Title>

        <Card title="Add New Student" style={{ marginBottom: '24px' }}>
          <div style={{ display: 'flex', gap: '12px', flexWrap: 'wrap', alignItems: 'flex-end' }}>
            <div>
              <div style={{ marginBottom: '4px', fontSize: '14px' }}>Name</div>
              <Input
                placeholder="Enter student name"
                value={newStudentName}
                onChange={(e) => setNewStudentName(e.target.value)}
                style={{ width: '200px' }}
              />
            </div>
            <div>
              <div style={{ marginBottom: '4px', fontSize: '14px' }}>Height (cm)</div>
              <InputNumber
                placeholder="Height"
                min={0}
                step={0.1}
                value={newStudentHeight}
                onChange={(value) => setNewStudentHeight(value)}
                style={{ width: '120px' }}
              />
            </div>
            <div>
              <div style={{ marginBottom: '4px', fontSize: '14px' }}>Weight (kg)</div>
              <InputNumber
                placeholder="Weight"
                min={0}
                step={0.1}
                value={newStudentWeight}
                onChange={(value) => setNewStudentWeight(value)}
                style={{ width: '120px' }}
              />
            </div>
            <Button type="primary" onClick={handleAddStudent}>
              Add Student
            </Button>
          </div>
        </Card>

        <Card title="Students List">
          <Input.Search
            placeholder="Search by name"
            allowClear
            value={searchTerm}
            onChange={handleSearchChange}
            style={{ marginBottom: '16px', maxWidth: '400px' }}
          />
          {error && <div style={{ color: '#ff4d4f', marginBottom: '16px' }}>{error}</div>}
          <Table
            dataSource={rows}
            loading={loading}
            rowKey="id"
            columns={[
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
            ]}
            pagination={{
              current: page,
              pageSize: pageSize,
              total: total,
              showSizeChanger: true,
              showTotal: (total) => `Total ${total} students`,
            }}
            onChange={handleTableChange}
          />
        </Card>
      </div>
    </>
  );
}
