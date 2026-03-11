import { useState, useMemo } from 'react';
import { Button, Tabs, Typography, Space, Badge, Empty, Table, Modal, Form, Input, Select, message } from 'antd';
import { ReloadOutlined, PlusOutlined, FilterOutlined, CalendarOutlined } from '@ant-design/icons';
import type { CSSProperties } from 'react';

interface TruckFormData {
  truckNumber: string;
  driverName: string;
  buildingId: string;
  status: string;
}

interface TruckLog extends TruckFormData {
  timestamp: number;
  totalTime: string;
}

export default function GeneratedApp() {
  const [messageApi, contextHolder] = message.useMessage();
  
  const [activeTab, setActiveTab] = useState<string>('traffic_control');
  const [addTruckModalVisible, setAddTruckModalVisible] = useState<boolean>(false);
  const [truckFormData, setTruckFormData] = useState<TruckFormData>({
    truckNumber: '',
    driverName: '',
    buildingId: '',
    status: 'Yard'
  });
  const [truckLogs, setTruckLogs] = useState<TruckLog[]>([]);
  const [yardVehicles, setYardVehicles] = useState<TruckFormData[]>([]);
  const [inboundVehicles, setInboundVehicles] = useState<TruckFormData[]>([]);
  const [outboundVehicles, setOutboundVehicles] = useState<TruckFormData[]>([]);
  const [fuelVehicles, setFuelVehicles] = useState<TruckFormData[]>([]);
  const [scrapVehicles, setScrapVehicles] = useState<TruckFormData[]>([]);
  const [selectedCategory, setSelectedCategory] = useState<string>('Yard');
  const [searchText, setSearchText] = useState<string>('');

  const [form] = Form.useForm();

  const yardCount = useMemo(() => yardVehicles.length, [yardVehicles]);
  const inboundCount = useMemo(() => inboundVehicles.length, [inboundVehicles]);
  const outboundCount = useMemo(() => outboundVehicles.length, [outboundVehicles]);
  const fuelCount = useMemo(() => fuelVehicles.length, [fuelVehicles]);
  const scrapCount = useMemo(() => scrapVehicles.length, [scrapVehicles]);
  
  const filteredTruckLogs = useMemo(() => {
    if (!searchText) return truckLogs;
    return truckLogs.filter(log => 
      log.truckNumber.includes(searchText) || log.driverName.includes(searchText)
    );
  }, [truckLogs, searchText]);

  const handleTabChange = (key: string) => {
    setActiveTab(key);
  };

  const actionSwitchToTrafficControl = () => {
    setActiveTab('traffic_control');
  };

  const actionSwitchToLogs = () => {
    setActiveTab('logs');
  };

  const actionOpenAddTruckModal = () => {
    setAddTruckModalVisible(true);
  };

  const actionCloseAddTruckModal = () => {
    setAddTruckModalVisible(false);
    setTruckFormData({ truckNumber: '', driverName: '', buildingId: '', status: 'Yard' });
    form.resetFields();
  };

  const actionSubmitTruckForm = () => {
    if (!truckFormData.truckNumber || !truckFormData.driverName || !truckFormData.buildingId) {
      messageApi.error('Failed to add truck. Please fill all required fields.');
      return;
    }

    const newLog: TruckLog = {
      ...truckFormData,
      timestamp: Date.now(),
      totalTime: '0h 0m'
    };

    setTruckLogs([...truckLogs, newLog]);

    if (truckFormData.status === 'Yard') {
      setYardVehicles([...yardVehicles, truckFormData]);
    } else if (truckFormData.status === 'Inbound') {
      setInboundVehicles([...inboundVehicles, truckFormData]);
    } else if (truckFormData.status === 'Outbound') {
      setOutboundVehicles([...outboundVehicles, truckFormData]);
    } else if (truckFormData.status === 'Fuel') {
      setFuelVehicles([...fuelVehicles, truckFormData]);
    } else if (truckFormData.status === 'Scrap') {
      setScrapVehicles([...scrapVehicles, truckFormData]);
    }

    setAddTruckModalVisible(false);
    setTruckFormData({ truckNumber: '', driverName: '', buildingId: '', status: 'Yard' });
    form.resetFields();
    messageApi.success('Truck added successfully');
  };

  const actionSelectYard = () => {
    setSelectedCategory('Yard');
  };

  const actionSelectInbound = () => {
    setSelectedCategory('Inbound');
  };

  const actionSelectOutbound = () => {
    setSelectedCategory('Outbound');
  };

  const actionSelectFuel = () => {
    setSelectedCategory('Fuel');
  };

  const actionSelectScrap = () => {
    setSelectedCategory('Scrap');
  };

  const rootContainerStyle: CSSProperties = {
    width: '100vw',
    height: '100vh',
    display: 'flex',
    flexDirection: 'column',
    overflow: 'hidden'
  };

  const tabsContainerStyle: CSSProperties = {
    height: '100%',
    display: 'flex',
    flexDirection: 'column'
  };

  const trafficControlContentStyle: CSSProperties = {
    display: 'flex',
    height: '100%',
    padding: '24px',
    gap: '24px',
    overflow: 'hidden'
  };

  const trafficPanelHeaderStyle: CSSProperties = {
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: '24px'
  };

  const leftPanelStyle: CSSProperties = {
    width: '400px',
    display: 'flex',
    flexDirection: 'column',
    gap: '12px'
  };

  const rightPanelStyle: CSSProperties = {
    flex: 1,
    border: '1px solid #e8e8e8',
    borderRadius: '8px',
    padding: '24px',
    display: 'flex',
    flexDirection: 'column',
    alignItems: 'center',
    justifyContent: 'center',
    backgroundColor: '#fafafa'
  };

  const inYardHeaderStyle: CSSProperties = {
    display: 'flex',
    alignItems: 'center',
    gap: '12px',
    marginBottom: '24px'
  };

  const logsContentStyle: CSSProperties = {
    padding: '24px',
    height: '100%',
    display: 'flex',
    flexDirection: 'column'
  };

  const logsHeaderStyle: CSSProperties = {
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: '24px'
  };

  const formActionsStyle: CSSProperties = {
    width: '100%',
    justifyContent: 'flex-end',
    marginTop: '24px'
  };

  const columns = [
    {
      title: 'Truck Number',
      dataIndex: 'truckNumber',
      key: 'truckNumber',
      sorter: (a: TruckLog, b: TruckLog) => a.truckNumber.localeCompare(b.truckNumber)
    },
    {
      title: 'Driver Name',
      dataIndex: 'driverName',
      key: 'driverName',
      sorter: (a: TruckLog, b: TruckLog) => a.driverName.localeCompare(b.driverName)
    },
    {
      title: 'Building ID',
      dataIndex: 'buildingId',
      key: 'buildingId',
      sorter: (a: TruckLog, b: TruckLog) => a.buildingId.localeCompare(b.buildingId)
    },
    {
      title: 'Status',
      dataIndex: 'status',
      key: 'status',
      sorter: (a: TruckLog, b: TruckLog) => a.status.localeCompare(b.status)
    },
    {
      title: 'Total Time',
      dataIndex: 'totalTime',
      key: 'totalTime',
      sorter: (a: TruckLog, b: TruckLog) => a.totalTime.localeCompare(b.totalTime)
    }
  ];

  const trafficControlContent = (
    <div style={trafficControlContentStyle}>
      <div style={leftPanelStyle}>
        <Button
          block
          size="large"
          type={selectedCategory === 'Yard' ? 'primary' : 'default'}
          style={{
            textAlign: 'left',
            height: '56px',
            fontSize: '16px',
            display: 'flex',
            justifyContent: 'space-between',
            alignItems: 'center'
          }}
          onClick={actionSelectYard}
        >
          <span>Yard</span>
          <Badge count={yardCount} showZero style={{ backgroundColor: '#faad14' }} />
        </Button>
        <Button
          block
          size="large"
          type={selectedCategory === 'Inbound' ? 'primary' : 'default'}
          style={{
            textAlign: 'left',
            height: '56px',
            fontSize: '16px'
          }}
          onClick={actionSelectInbound}
        >
          <span>Inbound</span>
          <Badge count={inboundCount} showZero style={{ backgroundColor: '#faad14' }} />
        </Button>
        <Button
          block
          size="large"
          type={selectedCategory === 'Outbound' ? 'primary' : 'default'}
          style={{
            textAlign: 'left',
            height: '56px',
            fontSize: '16px'
          }}
          onClick={actionSelectOutbound}
        >
          <span>Outbound</span>
          <Badge count={outboundCount} showZero style={{ backgroundColor: '#faad14' }} />
        </Button>
        <Button
          block
          size="large"
          type={selectedCategory === 'Fuel' ? 'primary' : 'default'}
          style={{
            textAlign: 'left',
            height: '56px',
            fontSize: '16px'
          }}
          onClick={actionSelectFuel}
        >
          <span>Fuel</span>
          <Badge count={fuelCount} showZero style={{ backgroundColor: '#faad14' }} />
        </Button>
        <Button
          block
          size="large"
          type={selectedCategory === 'Scrap' ? 'primary' : 'default'}
          style={{
            textAlign: 'left',
            height: '56px',
            fontSize: '16px'
          }}
          onClick={actionSelectScrap}
        >
          <span>Scrap</span>
          <Badge count={scrapCount} showZero style={{ backgroundColor: '#faad14' }} />
        </Button>
      </div>
      <div style={rightPanelStyle}>
        <div style={inYardHeaderStyle}>
          <Typography.Title level={4} style={{ margin: 0 }}>
            In Yard
          </Typography.Title>
          <Badge count={yardCount} showZero style={{ backgroundColor: '#faad14' }} />
        </div>
        <Empty description="There is no data to show you right now" image={Empty.PRESENTED_IMAGE_SIMPLE} />
      </div>
    </div>
  );

  const logsContent = (
    <div style={logsContentStyle}>
      <div style={logsHeaderStyle}>
        <Typography.Title level={3} style={{ margin: 0 }}>
          Truck Logs
        </Typography.Title>
        <Space size="middle">
          <Input.Search
            placeholder="Search..."
            style={{ width: '250px' }}
            allowClear
            value={searchText}
            onChange={(e) => setSearchText(e.target.value)}
          />
          <Button icon={<FilterOutlined />} type="default" />
          <Button icon={<CalendarOutlined />} type="default" />
        </Space>
      </div>
      <Table
        dataSource={filteredTruckLogs}
        columns={columns}
        pagination={{
          pageSize: 10,
          showSizeChanger: true,
          showTotal: (total) => `Total ${total} items`
        }}
        locale={{ emptyText: 'No data' }}
        style={{ flex: 1 }}
        rowKey={(record) => `${record.truckNumber}-${record.timestamp}`}
      />
    </div>
  );

  const tabItems = [
    {
      key: 'traffic_control',
      label: 'Traffic Control',
      children: trafficControlContent
    },
    {
      key: 'logs',
      label: 'Logs',
      children: logsContent
    }
  ];

  return (
    <div style={rootContainerStyle}>
      {contextHolder}
      <div style={trafficPanelHeaderStyle}>
        <Typography.Title level={2} style={{ margin: 0, padding: '24px 24px 0 24px' }}>
          Traffic Panel
        </Typography.Title>
        <Space size="middle" style={{ padding: '24px 24px 0 24px' }}>
          <Button icon={<ReloadOutlined />} type="default">
            Refresh
          </Button>
          <Button type="primary" icon={<PlusOutlined />} onClick={actionOpenAddTruckModal}>
            Add Truck
          </Button>
        </Space>
      </div>
      <Tabs
        activeKey={activeTab}
        onChange={handleTabChange}
        style={tabsContainerStyle}
        items={tabItems}
      />
      <Modal
        title="Add Truck"
        open={addTruckModalVisible}
        onCancel={actionCloseAddTruckModal}
        footer={null}
        width={500}
      >
        <Form
          form={form}
          layout="vertical"
          onFinish={actionSubmitTruckForm}
        >
          <Form.Item
            label="Truck Number"
            name="truckNumber"
            rules={[{ required: true, message: 'Please enter truck number' }]}
          >
            <Input
              placeholder="Enter truck number"
              value={truckFormData.truckNumber}
              onChange={(e) => setTruckFormData({ ...truckFormData, truckNumber: e.target.value })}
            />
          </Form.Item>
          <Form.Item
            label="Driver Name"
            name="driverName"
            rules={[{ required: true, message: 'Please enter driver name' }]}
          >
            <Input
              placeholder="Enter driver name"
              value={truckFormData.driverName}
              onChange={(e) => setTruckFormData({ ...truckFormData, driverName: e.target.value })}
            />
          </Form.Item>
          <Form.Item
            label="Building ID"
            name="buildingId"
            rules={[{ required: true, message: 'Please enter building ID' }]}
          >
            <Input
              placeholder="Enter building ID"
              value={truckFormData.buildingId}
              onChange={(e) => setTruckFormData({ ...truckFormData, buildingId: e.target.value })}
            />
          </Form.Item>
          <Form.Item
            label="Status"
            name="status"
            rules={[{ required: true, message: 'Please select status' }]}
            initialValue="Yard"
          >
            <Select
              placeholder="Select status"
              value={truckFormData.status}
              onChange={(value) => setTruckFormData({ ...truckFormData, status: value })}
              options={[
                { label: 'Yard', value: 'Yard' },
                { label: 'Inbound', value: 'Inbound' },
                { label: 'Outbound', value: 'Outbound' },
                { label: 'Fuel', value: 'Fuel' },
                { label: 'Scrap', value: 'Scrap' }
              ]}
            />
          </Form.Item>
          <Space style={formActionsStyle}>
            <Button type="default" onClick={actionCloseAddTruckModal}>
              Cancel
            </Button>
            <Button type="primary" htmlType="submit">
              Add Truck
            </Button>
          </Space>
        </Form>
      </Modal>
    </div>
  );
}
