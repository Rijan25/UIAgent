import { useState, useMemo } from 'react';
import { Card, Typography, Input, Select, Button, Modal, message, Tag, Statistic } from 'antd';
import type { CSSProperties } from 'react';

interface Truck {
  id: string;
  model: string;
  color: string;
  status: string;
  driver: string | null;
  lastMaintenance: string;
  mileage: number;
}

interface Driver {
  id: string;
  name: string;
  license: string;
  status: string;
  rating: number;
}

export default function GeneratedApp() {
  const [messageApi, contextHolder] = message.useMessage();

  const [trucks, setTrucks] = useState<Truck[]>([
    {
      id: "T001",
      model: "Volvo FH16",
      color: "White",
      status: "available",
      driver: null,
      lastMaintenance: "2024-01-15",
      mileage: 45000
    },
    {
      id: "T002",
      model: "Scania R500",
      color: "Black",
      status: "occupied",
      driver: "John Smith",
      lastMaintenance: "2024-01-10",
      mileage: 52000
    },
    {
      id: "T003",
      model: "Mercedes Actros",
      color: "Silver",
      status: "available",
      driver: null,
      lastMaintenance: "2024-01-20",
      mileage: 38000
    },
    {
      id: "T004",
      model: "MAN TGX",
      color: "White",
      status: "unassigned",
      driver: null,
      lastMaintenance: "2024-01-05",
      mileage: 61000
    },
    {
      id: "T005",
      model: "DAF XF",
      color: "Gray",
      status: "occupied",
      driver: "Sarah Johnson",
      lastMaintenance: "2024-01-18",
      mileage: 47000
    },
    {
      id: "T006",
      model: "Iveco Stralis",
      color: "Black",
      status: "available",
      driver: null,
      lastMaintenance: "2024-01-22",
      mileage: 33000
    },
    {
      id: "T007",
      model: "Volvo FH16",
      color: "Silver",
      status: "unassigned",
      driver: null,
      lastMaintenance: "2024-01-12",
      mileage: 55000
    },
    {
      id: "T008",
      model: "Scania R500",
      color: "White",
      status: "available",
      driver: null,
      lastMaintenance: "2024-01-25",
      mileage: 29000
    }
  ]);

  const [drivers] = useState<Driver[]>([
    {
      id: "D001",
      name: "Michael Brown",
      license: "CDL-A",
      status: "available",
      rating: 4.8
    },
    {
      id: "D002",
      name: "Emily Davis",
      license: "CDL-A",
      status: "available",
      rating: 4.9
    },
    {
      id: "D003",
      name: "Robert Wilson",
      license: "CDL-B",
      status: "available",
      rating: 4.6
    },
    {
      id: "D004",
      name: "Jennifer Martinez",
      license: "CDL-A",
      status: "available",
      rating: 4.7
    },
    {
      id: "D005",
      name: "David Anderson",
      license: "CDL-A",
      status: "available",
      rating: 4.5
    }
  ]);

  const [selectedTruck, setSelectedTruck] = useState<Truck | null>(null);
  const [selectedDriver, setSelectedDriver] = useState<string | null>(null);
  const [filterColor, setFilterColor] = useState<string>("all");
  const [filterStatus, setFilterStatus] = useState<string>("all");
  const [searchQuery, setSearchQuery] = useState<string>("");
  const [assignmentModalVisible, setAssignmentModalVisible] = useState<boolean>(false);

  const filteredTrucks = useMemo(() => {
    return trucks.filter(t => 
      (filterColor === 'all' || t.color === filterColor) && 
      (filterStatus === 'all' || t.status === filterStatus) && 
      (searchQuery === '' || t.id.includes(searchQuery) || t.model.toLowerCase().includes(searchQuery.toLowerCase()))
    );
  }, [trucks, filterColor, filterStatus, searchQuery]);

  const availableTrucksCount = useMemo(() => {
    return trucks.filter(t => t.status === 'available').length;
  }, [trucks]);

  const occupiedTrucksCount = useMemo(() => {
    return trucks.filter(t => t.status === 'occupied').length;
  }, [trucks]);

  const unassignedTrucksCount = useMemo(() => {
    return trucks.filter(t => t.status === 'unassigned').length;
  }, [trucks]);

  const availableDrivers = useMemo(() => {
    return drivers.filter(d => d.status === 'available');
  }, [drivers]);

  const onColorFilterChange = (color: string) => {
    setFilterColor(color);
  };

  const onStatusFilterChange = (status: string) => {
    setFilterStatus(status);
  };

  const onSearchChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setSearchQuery(e.target.value);
  };

  const onDriverSelect = (driverId: string) => {
    setSelectedDriver(driverId);
  };

  const onOpenAssignmentModal = (truck: Truck) => {
    setAssignmentModalVisible(true);
    setSelectedTruck(truck);
  };

  const onCloseAssignmentModal = () => {
    setAssignmentModalVisible(false);
    setSelectedTruck(null);
    setSelectedDriver(null);
  };

  const onAssignDriver = () => {
    if (!selectedTruck || !selectedDriver) {
      messageApi.error('Please select a driver');
      return;
    }

    const driver = drivers.find(d => d.id === selectedDriver);
    if (!driver) {
      messageApi.error('Driver not found');
      return;
    }

    setTrucks(trucks.map(t => 
      t.id === selectedTruck.id 
        ? {...t, driver: driver.name, status: 'occupied'} 
        : t
    ));
    
    messageApi.success('Driver assigned successfully');
    setAssignmentModalVisible(false);
    setSelectedTruck(null);
    setSelectedDriver(null);
  };

  const onUnassignDriver = (truckId: string) => {
    setTrucks(trucks.map(t => 
      t.id === truckId 
        ? {...t, driver: null, status: 'available'} 
        : t
    ));
    messageApi.success('Driver unassigned successfully');
  };

  const getStatusColor = (status: string): string => {
    switch (status) {
      case 'available':
        return 'green';
      case 'occupied':
        return 'blue';
      case 'unassigned':
        return 'orange';
      default:
        return 'default';
    }
  };

  const rootContainerStyle: CSSProperties = {
    width: "100vw",
    height: "100vh",
    backgroundColor: "#f5f5f5",
    overflow: "hidden",
    display: "flex",
    flexDirection: "column"
  };

  const headerSectionStyle: CSSProperties = {
    backgroundColor: "#2c2c2c",
    padding: "24px 32px",
    borderBottom: "1px solid #1a1a1a"
  };

  const pageTitleStyle: CSSProperties = {
    color: "#ffffff",
    margin: 0,
    fontWeight: 300,
    letterSpacing: "0.5px"
  };

  const statsContainerStyle: CSSProperties = {
    display: "flex",
    gap: "16px",
    marginTop: "16px"
  };

  const statCardStyle: CSSProperties = {
    flex: 1,
    backgroundColor: "#ffffff",
    border: "1px solid #e0e0e0"
  };

  const mainContentStyle: CSSProperties = {
    flex: 1,
    padding: "32px",
    overflow: "auto"
  };

  const filtersSectionStyle: CSSProperties = {
    display: "flex",
    gap: "16px",
    marginBottom: "24px",
    alignItems: "center",
    backgroundColor: "#ffffff",
    padding: "20px",
    border: "1px solid #e0e0e0"
  };

  const trucksGridStyle: CSSProperties = {
    display: "grid",
    gridTemplateColumns: "repeat(auto-fill, minmax(320px, 1fr))",
    gap: "20px"
  };

  const truckCardStyle: CSSProperties = {
    backgroundColor: "#ffffff",
    border: "1px solid #e0e0e0",
    transition: "all 0.3s"
  };

  const modalContentStyle: CSSProperties = {
    padding: "20px 0"
  };

  const truckInfoSectionStyle: CSSProperties = {
    marginBottom: "24px",
    padding: "16px",
    backgroundColor: "#fafafa",
    border: "1px solid #e0e0e0"
  };

  const assignButtonStyle: CSSProperties = {
    backgroundColor: "#2c2c2c",
    borderColor: "#2c2c2c"
  };

  return (
    <>
      {contextHolder}
      <div style={rootContainerStyle}>
        <div style={headerSectionStyle}>
          <Typography.Title level={2} style={pageTitleStyle}>
            Truck and Driver Assignment
          </Typography.Title>
          <div style={statsContainerStyle}>
            <Card size="small" style={statCardStyle}>
              <Statistic 
                title="Available" 
                value={availableTrucksCount} 
                valueStyle={{ color: '#52c41a' }}
              />
            </Card>
            <Card size="small" style={statCardStyle}>
              <Statistic 
                title="Occupied" 
                value={occupiedTrucksCount} 
                valueStyle={{ color: '#1890ff' }}
              />
            </Card>
            <Card size="small" style={statCardStyle}>
              <Statistic 
                title="Unassigned" 
                value={unassignedTrucksCount} 
                valueStyle={{ color: '#fa8c16' }}
              />
            </Card>
          </div>
        </div>

        <div style={mainContentStyle}>
          <div style={filtersSectionStyle}>
            <Input.Search
              placeholder="Search by truck ID or model"
              allowClear
              value={searchQuery}
              onChange={onSearchChange}
              style={{ width: "300px" }}
            />
            <Select
              placeholder="Filter by color"
              value={filterColor}
              onChange={onColorFilterChange}
              style={{ width: "180px" }}
              options={[
                { label: "All Colors", value: "all" },
                { label: "White", value: "White" },
                { label: "Black", value: "Black" },
                { label: "Silver", value: "Silver" },
                { label: "Gray", value: "Gray" }
              ]}
            />
            <Select
              placeholder="Filter by status"
              value={filterStatus}
              onChange={onStatusFilterChange}
              style={{ width: "180px" }}
              options={[
                { label: "All Status", value: "all" },
                { label: "Available", value: "available" },
                { label: "Occupied", value: "occupied" },
                { label: "Unassigned", value: "unassigned" }
              ]}
            />
          </div>

          <div style={trucksGridStyle}>
            {filteredTrucks.map((truck) => (
              <Card
                key={truck.id}
                hoverable
                style={truckCardStyle}
                title={
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                    <span>{truck.id}</span>
                    <Tag color={getStatusColor(truck.status)}>{truck.status.toUpperCase()}</Tag>
                  </div>
                }
              >
                <div style={{ marginBottom: '12px' }}>
                  <Typography.Text strong>Model: </Typography.Text>
                  <Typography.Text>{truck.model}</Typography.Text>
                </div>
                <div style={{ marginBottom: '12px' }}>
                  <Typography.Text strong>Color: </Typography.Text>
                  <Typography.Text>{truck.color}</Typography.Text>
                </div>
                <div style={{ marginBottom: '12px' }}>
                  <Typography.Text strong>Mileage: </Typography.Text>
                  <Typography.Text>{truck.mileage.toLocaleString()} km</Typography.Text>
                </div>
                <div style={{ marginBottom: '12px' }}>
                  <Typography.Text strong>Last Maintenance: </Typography.Text>
                  <Typography.Text>{truck.lastMaintenance}</Typography.Text>
                </div>
                {truck.driver && (
                  <div style={{ marginBottom: '12px' }}>
                    <Typography.Text strong>Driver: </Typography.Text>
                    <Typography.Text>{truck.driver}</Typography.Text>
                  </div>
                )}
                <div style={{ marginTop: '16px', display: 'flex', gap: '8px' }}>
                  {truck.status === 'available' && (
                    <Button
                      type="primary"
                      size="small"
                      block
                      style={assignButtonStyle}
                      onClick={() => onOpenAssignmentModal(truck)}
                    >
                      Assign Driver
                    </Button>
                  )}
                  {truck.status === 'occupied' && (
                    <Button
                      danger
                      size="small"
                      block
                      onClick={() => onUnassignDriver(truck.id)}
                    >
                      Unassign
                    </Button>
                  )}
                </div>
              </Card>
            ))}
          </div>
        </div>

        <Modal
          title="Assign Driver to Truck"
          open={assignmentModalVisible}
          onCancel={onCloseAssignmentModal}
          footer={null}
          width={600}
        >
          <div style={modalContentStyle}>
            {selectedTruck && (
              <>
                <div style={truckInfoSectionStyle}>
                  <Typography.Title level={5}>Truck Information</Typography.Title>
                  <div style={{ marginBottom: '8px' }}>
                    <Typography.Text strong>ID: </Typography.Text>
                    <Typography.Text>{selectedTruck.id}</Typography.Text>
                  </div>
                  <div style={{ marginBottom: '8px' }}>
                    <Typography.Text strong>Model: </Typography.Text>
                    <Typography.Text>{selectedTruck.model}</Typography.Text>
                  </div>
                  <div style={{ marginBottom: '8px' }}>
                    <Typography.Text strong>Color: </Typography.Text>
                    <Typography.Text>{selectedTruck.color}</Typography.Text>
                  </div>
                  <div>
                    <Typography.Text strong>Mileage: </Typography.Text>
                    <Typography.Text>{selectedTruck.mileage.toLocaleString()} km</Typography.Text>
                  </div>
                </div>

                <Select
                  placeholder="Select an available driver"
                  value={selectedDriver}
                  onChange={onDriverSelect}
                  style={{ width: "100%", marginBottom: "20px" }}
                  options={availableDrivers.map(driver => ({
                    label: `${driver.name} - ${driver.license} (Rating: ${driver.rating})`,
                    value: driver.id
                  }))}
                />

                <Button
                  type="primary"
                  block
                  size="large"
                  style={assignButtonStyle}
                  onClick={onAssignDriver}
                  disabled={!selectedDriver}
                >
                  Assign Driver
                </Button>
              </>
            )}
          </div>
        </Modal>
      </div>
    </>
  );
}
