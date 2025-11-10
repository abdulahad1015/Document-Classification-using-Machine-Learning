import React from 'react';

const Sidebar = ({ open, active, onSelect }) => {
  return (
    <aside className={`sidebar ${open ? 'open' : 'closed'}`}>
      <ul>
        {['Dashboard', 'Upload', 'My Files', 'Settings'].map((item) => (
          <li
            key={item}
            className={active === item ? 'active' : ''}
            onClick={() => onSelect(item)}
            role="button"
            tabIndex={0}
          >
            {item}
          </li>
        ))}
      </ul>
    </aside>
  );
};

export default Sidebar;