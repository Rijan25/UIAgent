import { useEffect, useState, useMemo } from 'react';
import { Button, Card, Form, Input, Modal, Table, Typography, message } from 'antd';
import type { TableProps } from 'antd';
import type { CSSProperties } from 'react';
import initSqlJs from 'sql.js';
import type { Database } from 'sql.js';

const { Title } = Typography;

interface Student {
  id: number;
  name: string;
  height: number;
  weight: number;
  marks: number;
}

export default function GeneratedApp() {
  const [messageApi, contextHolder] = message.useMessage();
  
  const [rows, setRows] = useState<Student[]>([]);
  const [loading, setLoading] = useState<boolean>(false);
  const [error, setError] = useState<string>('');
  const [page, setPage] = useState<number>(1);
  const [pageSize, setPageSize] = useState<number>(50);
  const [total, setTotal] = useState<number>(0);
  const [heightMin, setHeightMin] = useState<number>(0);
  const [heightMax, setHeightMax] = useState<number>(300);
  const [sortField, setSortField] = useState<string>('marks');
  const [sortOrder, setSortOrder] = useState<string>('desc');
  const [modalVisible, setModalVisible] = useState<boolean>(false);
  const [editingStudent, setEditingStudent] = useState<Student | null>(null);
  const [formName, setFormName] = useState<string>('');
  const [formHeight, setFormHeight] = useState<number>(0);
  const [formWeight, setFormWeight] = useState<number>(0);
  const [formMarks, setFormMarks] = useState<number>(0);
  const [searchTerm] = useState<string>('');
  
  const [db, setDb] = useState<Database | null>(null);

  useEffect(() => {
    const initDb = async () => {
      try {
        setLoading(true);
        const SQL = await initSqlJs({ locateFile: () => '/db/sql-wasm.wasm' });
        const response = await fetch('/db/student_data.db');
        const buffer = await response.arrayBuffer();
        const database = new SQL.Database(new Uint8Array(buffer));
        setDb(database);
        setLoading(false);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to initialize database');
        setLoading(false);
      }
    };
    initDb();
  }, []);

  useEffect(() => {
    if (!db) return;
    
    const fetchData = async () => {
      try {
        setLoading(true);
        setError('');
        
        const currentPage = Number(page);
        const currentPageSize = Number(pageSize);
        const currentHeightMin = Number(heightMin);
        const currentHeightMax = Number(heightMax);
        
        const validPage = Number.isInteger(currentPage) && currentPage > 0 ? currentPage : 1;
        const validPageSize = Number.isInteger(currentPageSize) && currentPageSize > 0 ? currentPageSize : 50;
        const validHeightMin = !isNaN(currentHeightMin) ? currentHeightMin : 0;
        const validHeightMax = !isNaN(currentHeightMax) ? currentHeightMax : 300;
        
        const offset = (validPage - 1) * validPageSize;
        
        const countSql = `SELECT COUNT(*) as count FROM student_data sd LEFT JOIN student_marks sm ON sd.id = sm.student_id WHERE (:search = '' OR sd.name LIKE '%' || :search || '%') AND sd.height >= :heightMin AND sd.height <= :heightMax`;
        const countStmt = db.prepare(countSql);
        countStmt.bind({
          ':search': searchTerm,
          ':heightMin': validHeightMin,
          ':heightMax': validHeightMax
        });
        countStmt.step();
        const countRow = countStmt.getAsObject();
        const totalCount = (countRow.count as number) || 0;
        countStmt.free();
        
        const dataSql = `SELECT sd.id, sd.name, sd.height, sd.weight, (sm.nepali + sm.english + sm.mathematics + sm.science + sm.social_studies) AS marks FROM student_data sd LEFT JOIN student_marks sm ON sd.id = sm.student_id WHERE (:search = '' OR sd.name LIKE '%' || :search || '%') AND sd.height >= :heightMin AND sd.height <= :heightMax ORDER BY marks DESC LIMIT ${validPageSize} OFFSET ${offset}`;
        const dataStmt = db.prepare(dataSql);
        dataStmt.bind({
          ':search': searchTerm,
          ':heightMin': validHeightMin,
          ':heightMax': validHeightMax
        });
        
        const results: Student[] = [];
        while (dataStmt.step()) {
          const row = dataStmt.get();
          results.push({
            id: row[0] as number,
            name: row[1] as string,
            height: row[2] as number,
            weight: row[3] as number,
            marks: (row[4] as number) || 0
          });
        }
        dataStmt.free();
        
        setRows(results);
        setTotal(totalCount);
        setLoading(false);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to fetch data');
        setLoading(false);
      }
    };
    
    fetchData();
  }, [db, page, pageSize, heightMin, heightMax, searchTerm]);

  const filteredRows = useMemo(() => {
    const min = Number(heightMin);
    const max = Number(heightMax);
    const validMin = !isNaN(min) ? min : 0;
    const validMax = !isNaN(max) ? max : 300;
    return rows.filter(r => r.height >= validMin && r.height <= validMax);
  }, [rows, heightMin, heightMax]);

  const sortedRows = useMemo(() => {
    const sorted = [...filteredRows];
    sorted.sort((a, b) => {
      const aVal = a[sortField as keyof Student] as number;
      const bVal = b[sortField as keyof Student] as number;
      return sortOrder === 'asc' ? aVal - bVal : bVal - aVal;
    });
    return sorted;
  }, [filteredRows, sortField, sortOrder]);

  const handleOpenAddModal = () => {
    setModalVisible(true);
    setEditingStudent(null);
    setFormName('');
    setFormHeight(0);
    setFormWeight(0);
    setFormMarks(0);
  };

  const handleOpenEditModal = (student: Student) => {
    setModalVisible(true);
    setEditingStudent(student);
    setFormName(student.name);
    setFormHeight(student.height);
    setFormWeight(student.weight);
    setFormMarks(student.marks);
  };

  const handleCloseModal = () => {
    setModalVisible(false);
  };

  const handleAddStudent = () => {
    if (!formName) {
      messageApi.error('Name is required');
      return;
    }
    const newStudent: Student = {
      id: Date.now(),
      name: formName,
      height: formHeight,
      weight: formWeight,
      marks: formMarks
    };
    setRows([...rows, newStudent]);
    setModalVisible(false);
    messageApi.success('Student added successfully');
  };

  const handleEditStudent = () => {
    if (!formName) {
      messageApi.error('Name is required');
      return;
    }
    if (!editingStudent) return;
    
    setRows(rows.map(r => 
      r.id === editingStudent.id 
        ? { ...r, name: formName, height: formHeight, weight: formWeight, marks: formMarks }
        : r
    ));
    setModalVisible(false);
    messageApi.success('Student updated successfully');
  };

  const handleDeleteStudent = (studentId: number) => {
    Modal.confirm({
      title: 'Are you sure you want to delete this student?',
      onOk: () => {
        setRows(rows.filter(r => r.id !== studentId));
        messageApi.success('Student deleted successfully');
      }
    });
  };

  const handleTableChange: TableProps<Student>['onChange'] = (pagination, _filters, sorter) => {
    const currentPage = pagination.current ?? 1;
    const currentPageSize = pagination.pageSize ?? 50;
    setPage(currentPage);
    setPageSize(currentPageSize);
    
    if (sorter && !Array.isArray(sorter) && sorter.field && sorter.order) {
      setSortField(sorter.field as string);
      setSortOrder(sorter.order === 'ascend' ? 'asc' : 'desc');
    }
  };

  const columns: TableProps<Student>['columns'] = [
    {
      title: 'Name',
      dataIndex: 'name',
      key: 'name',
      sorter: true
    },
    {
      title: 'Height',
      dataIndex: 'height',
      key: 'height',
      sorter: true
    },
    {
      title: 'Weight',
      dataIndex: 'weight',
      key: 'weight',
      sorter: true
    },
    {
      title: 'Marks',
      dataIndex: 'marks',
      key: 'marks',
      sorter: true
    },
    {
      title: 'Actions',
      key: 'actions',
      render: (_text, record) => (
        <div>
          <Button
            size="small"
            onClick={() => handleOpenEditModal(record)}
            style={{
              marginRight: '8px',
              backgroundColor: 'transparent',
              borderColor: '#e0e0e0',
              color: '#e0e0e0'
            }}
          >
            Edit
          </Button>
          <Button
            size="small"
            danger
            onClick={() => handleDeleteStudent(record.id)}
            style={{
              backgroundColor: 'transparent',
              borderColor: '#ff4d4f',
              color: '#ff4d4f'
            }}
          >
            Delete
          </Button>
        </div>
      )
    }
  ];

  const rootContainerStyle: CSSProperties = {
    width: '100vw',
    height: '100vh',
    backgroundColor: '#1a1a1a',
    color: '#e0e0e0',
    overflow: 'hidden',
    display: 'flex',
    flexDirection: 'column'
  };

  const mainSectionStyle: CSSProperties = {
    flex: 1,
    display: 'flex',
    flexDirection: 'column',
    padding: '32px',
    overflow: 'auto'
  };

  const headerCardStyle: CSSProperties = {
    backgroundColor: '#2d2d2d',
    border: '1px solid #3d3d3d',
    marginBottom: '24px',
    boxShadow: 'none'
  };

  const headerContentStyle: CSSProperties = {
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center'
  };

  const titleStyle: CSSProperties = {
    color: '#e0e0e0',
    fontWeight: 300,
    letterSpacing: '0.5px',
    margin: 0
  };

  const addButtonStyle: CSSProperties = {
    backgroundColor: '#2d2d2d',
    borderColor: '#e0e0e0',
    color: '#e0e0e0',
    borderRadius: '2px',
    fontWeight: 400
  };

  const filterCardStyle: CSSProperties = {
    backgroundColor: '#2d2d2d',
    border: '1px solid #3d3d3d',
    marginBottom: '24px',
    boxShadow: 'none'
  };

  const inputStyle: CSSProperties = {
    backgroundColor: '#1a1a1a',
    borderColor: '#3d3d3d',
    color: '#e0e0e0',
    width: '150px'
  };

  const tableCardStyle: CSSProperties = {
    backgroundColor: '#2d2d2d',
    border: '1px solid #3d3d3d',
    flex: 1,
    display: 'flex',
    flexDirection: 'column',
    boxShadow: 'none'
  };

  const modalButtonsStyle: CSSProperties = {
    display: 'flex',
    justifyContent: 'flex-end',
    gap: '8px',
    marginTop: '24px'
  };

  const cancelButtonStyle: CSSProperties = {
    backgroundColor: 'transparent',
    borderColor: '#3d3d3d',
    color: '#e0e0e0'
  };

  const saveButtonStyle: CSSProperties = {
    backgroundColor: '#2d2d2d',
    borderColor: '#e0e0e0',
    color: '#e0e0e0'
  };

  return (
    <div style={rootContainerStyle}>
      {contextHolder}
      <div style={mainSectionStyle}>
        <Card bordered={false} style={headerCardStyle}>
          <div style={headerContentStyle}>
            <Title level={2} style={titleStyle}>
              Student Management
            </Title>
            <Button type="primary" onClick={handleOpenAddModal} style={addButtonStyle}>
              Add Student
            </Button>
          </div>
        </Card>

        <Card bordered={false} style={filterCardStyle}>
          <Form layout="inline">
            <Form.Item label="Min Height">
              <Input
                type="number"
                placeholder="Min Height"
                value={heightMin}
                onChange={(e) => setHeightMin(Number(e.target.value))}
                style={inputStyle}
              />
            </Form.Item>
            <Form.Item label="Max Height">
              <Input
                type="number"
                placeholder="Max Height"
                value={heightMax}
                onChange={(e) => setHeightMax(Number(e.target.value))}
                style={inputStyle}
              />
            </Form.Item>
          </Form>
        </Card>

        <Card bordered={false} style={tableCardStyle}>
          {error && <div style={{ color: '#ff4d4f', marginBottom: '16px' }}>{error}</div>}
          <Table
            columns={columns}
            dataSource={sortedRows}
            loading={loading}
            rowKey="id"
            pagination={{
              current: page,
              pageSize: pageSize,
              total: total,
              showSizeChanger: true
            }}
            onChange={handleTableChange}
            rowClassName={(record) => record.marks > 90 ? 'highlight-row' : ''}
          />
        </Card>
      </div>

      <Modal
        title={editingStudent ? 'Edit Student' : 'Add Student'}
        open={modalVisible}
        onCancel={handleCloseModal}
        footer={null}
      >
        <Form layout="vertical">
          <Form.Item label="Name" required>
            <Input
              placeholder="Enter student name"
              value={formName}
              onChange={(e) => setFormName(e.target.value)}
              style={{ backgroundColor: '#1a1a1a', borderColor: '#3d3d3d', color: '#e0e0e0' }}
            />
          </Form.Item>
          <Form.Item label="Height" required>
            <Input
              type="number"
              placeholder="Enter height"
              value={formHeight}
              onChange={(e) => setFormHeight(Number(e.target.value))}
              style={{ backgroundColor: '#1a1a1a', borderColor: '#3d3d3d', color: '#e0e0e0' }}
            />
          </Form.Item>
          <Form.Item label="Weight" required>
            <Input
              type="number"
              placeholder="Enter weight"
              value={formWeight}
              onChange={(e) => setFormWeight(Number(e.target.value))}
              style={{ backgroundColor: '#1a1a1a', borderColor: '#3d3d3d', color: '#e0e0e0' }}
            />
          </Form.Item>
          <Form.Item label="Marks" required>
            <Input
              type="number"
              placeholder="Enter marks"
              value={formMarks}
              onChange={(e) => setFormMarks(Number(e.target.value))}
              style={{ backgroundColor: '#1a1a1a', borderColor: '#3d3d3d', color: '#e0e0e0' }}
            />
          </Form.Item>
          <div style={modalButtonsStyle}>
            <Button onClick={handleCloseModal} style={cancelButtonStyle}>
              Cancel
            </Button>
            <Button
              type="primary"
              onClick={editingStudent ? handleEditStudent : handleAddStudent}
              style={saveButtonStyle}
            >
              Save
            </Button>
          </div>
        </Form>
      </Modal>
    </div>
  );
}
