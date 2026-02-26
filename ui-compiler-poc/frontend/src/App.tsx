import { useState } from 'react';
import { Button, Card, Badge, Typography } from 'antd';
import { ReloadOutlined, PlusOutlined } from '@ant-design/icons';
import type { CSSProperties } from 'react';

export default function GeneratedApp() {
  const [yardCount] = useState<number>(7);
  const [inboundCount] = useState<number>(2);

  const rootComponentStyle: CSSProperties = {
    display: 'flex',
    height: '100vh',
    backgroundColor: '#f5f5f5',
  };

  const sidebarStyle: CSSProperties = {
    width: '240px',
    backgroundColor: '#ffffff',
    borderRight: '1px solid #e8e8e8',
    padding: '16px',
    overflowY: 'auto',
  };

  const mainContentStyle: CSSProperties = {
    flex: '1',
    padding: '24px',
    overflowY: 'auto',
  };

  const headerStyle: CSSProperties = {
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: '24px',
  };

  const titleStyle: CSSProperties = {
    margin: '0',
  };

  const headerActionsStyle: CSSProperties = {
    display: 'flex',
    gap: '12px',
  };

  const contentLayoutStyle: CSSProperties = {
    display: 'flex',
    gap: '24px',
  };

  const leftPanelStyle: CSSProperties = {
    width: '400px',
    display: 'flex',
    flexDirection: 'column',
    gap: '16px',
  };

  const rightPanelStyle: CSSProperties = {
    flex: '1',
  };

  const inYardHeaderStyle: CSSProperties = {
    display: 'flex',
    alignItems: 'center',
    gap: '8px',
    marginBottom: '16px',
  };

  const inYardTitleStyle: CSSProperties = {
    margin: '0',
  };

  const truckGridStyle: CSSProperties = {
    display: 'grid',
    gridTemplateColumns: 'repeat(3, 1fr)',
    gap: '16px',
  };

  return (
    <div style={rootComponentStyle}>
      <div style={sidebarStyle}></div>
      <div style={mainContentStyle}>
        <div style={headerStyle}>
          <Typography.Title level={2} style={titleStyle}>
            Traffic Panel
          </Typography.Title>
          <div style={headerActionsStyle}>
            <Button icon={<ReloadOutlined />}>Refresh</Button>
            <Button type="primary" icon={<PlusOutlined />}>
              Add Truck
            </Button>
          </div>
        </div>
        <div style={contentLayoutStyle}>
          <div style={leftPanelStyle}>
            <Card title="Yard" extra={yardCount}></Card>
            <Card title="Inbound" extra={inboundCount}></Card>
            <Card title="Outbound"></Card>
            <Card title="Fuel"></Card>
            <Card title="Scrap"></Card>
          </div>
          <div style={rightPanelStyle}>
            <div>
              <div style={inYardHeaderStyle}>
                <Typography.Title level={4} style={inYardTitleStyle}>
                  In Yard
                </Typography.Title>
                <Badge count="7 Vehicle" />
              </div>
              <div style={truckGridStyle}>
                <Card size="small"></Card>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
