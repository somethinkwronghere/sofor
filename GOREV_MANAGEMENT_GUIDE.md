# Görev Yönetimi (Task Management) User Guide

## Overview
The Task Management module provides comprehensive functionality for managing personnel tasks, including creation, tracking, completion, and archival.

## Features

### 1. Draft Tasks (Görev Taslağı)
**URL:** `/gorev/taslak/`

View and manage tasks that are not yet completed (durum = NULL).

**Features:**
- View all draft tasks
- Search by destination, authority, description, or personnel name
- Filter by personnel, vehicle, or task location
- Filter by date range
- Edit tasks (admin only)
- Delete tasks (admin only)
- 25 tasks per page with pagination

**Columns Displayed:**
- Personnel (Personel)
- Task Location (Görev Yeri)
- Destination (Varış Yeri)
- Vehicle (Araç)
- Start Date (Başlangıç)
- End Date (Bitiş)
- Authority (Yetkili)
- Actions (İşlemler) - admin only

### 2. Completed Tasks (Nihai Liste)
**URL:** `/gorev/nihai/`

View tasks completed in the current month (durum = 1).

**Features:**
- View all completed tasks from current month
- Same search and filter options as draft tasks
- Edit capability (admin only)
- Status badge showing "Tamamlandı"
- Pagination

### 3. Last Month's Tasks (Geçen Ayki Görevler)
**URL:** `/gorev/gecen-ay/`

View all tasks from the previous month.

**Features:**
- Automatic date range calculation
- Shows date range at top of page
- Search and filter options
- Read-only view
- Status badges (Draft/Completed)
- Pagination

### 4. Archived Tasks (Eski Görevler)
**URL:** `/gorev/eski/`

View tasks older than 2 months.

**Features:**
- Archive notice at top
- Extended date filtering
- Search and filter options
- Read-only view
- Status badges
- Pagination

### 5. Add New Task (Yeni Görev Ekle)
**URL:** `/gorev/ekle/`  
**Access:** Admin only

Create a new task with the following fields:

**Required Fields:**
- Personnel (Personel) - Select from dropdown
- Task Location (Görev Yeri) - Select from dropdown
- Destination (Varış Yeri) - Text input
- Start Date (Başlangıç Tarihi) - DateTime picker
- Authority (Yetkili) - Text input

**Optional Fields:**
- Vehicle (Araç) - Select from dropdown
- End Date (Bitiş Tarihi) - DateTime picker
- Province Approval (İl Olur) - Text input
- Description (Açıklama) - Text area

**Validation Rules:**
- End date cannot be before start date
- All required fields must be filled
- Personnel and task location must be selected

**After Creation:**
- Task is saved as draft (durum = NULL)
- Log entry is created
- User is redirected to draft tasks list
- Success message is displayed

### 6. Edit Task (Görev Düzenle)
**URL:** `/gorev/duzenle/<id>/`  
**Access:** Admin only

Edit an existing task with pre-populated form.

**Additional Features:**
- Status dropdown (Draft/Completed)
- All fields can be updated
- Validation same as add form
- Log entry created on update

### 7. Delete Task (Görev Sil)
**URL:** `/gorev/sil/<id>/`  
**Access:** Admin only

Soft delete a task (sets gizle = True).

**Process:**
1. Click delete button on task row
2. Confirmation modal appears
3. Confirm deletion
4. Task is marked as hidden (not physically deleted)
5. Log entry is created
6. Task disappears from active lists

## Search and Filter Options

### Text Search
Search across multiple fields:
- Destination (Varış Yeri)
- Authority (Yetkili)
- Description (Açıklama)
- Personnel Name (Personel Adı)

### Filter Dropdowns
- **Personnel:** Filter by specific personnel member
- **Vehicle:** Filter by specific vehicle
- **Task Location:** Filter by specific location

### Date Range
- **Start Date:** Show tasks from this date onwards
- **End Date:** Show tasks up to this date

### Filter Actions
- **Filter Button:** Apply selected filters
- **Clear Button:** Reset all filters

## Pagination

- **Items per page:** 25
- **Navigation:** Previous/Next buttons
- **Page indicator:** Shows current page / total pages
- **Total count:** Displays total number of tasks found
- **Filter persistence:** Filters are maintained across pages

## Permission System

### Admin Users (yonetici = True)
- View all tasks
- Create new tasks
- Edit any task
- Delete any task
- Access all features

### Regular Users (yonetici = False)
- View only their own tasks
- Cannot create tasks
- Cannot edit tasks
- Cannot delete tasks
- Read-only access

## Status Badges

Tasks display status badges:
- **Taslak** (Draft) - Yellow badge - durum = NULL
- **Tamamlandı** (Completed) - Green badge - durum = 1

## Logging

All operations are logged:
- Task creation
- Task updates
- Task deletion
- Includes user, timestamp, and IP address

## Mobile Support

All views are responsive and work on:
- Desktop computers
- Tablets
- Mobile phones

## Tips for Best Use

1. **Use filters** to quickly find specific tasks
2. **Check draft tasks regularly** to track pending work
3. **Mark tasks as completed** when finished
4. **Use date filters** for reporting periods
5. **Search by personnel** to see individual workloads
6. **Review archived tasks** for historical data

## Keyboard Shortcuts

- **Tab:** Navigate between form fields
- **Enter:** Submit forms
- **Esc:** Close modals

## Common Workflows

### Creating a Task
1. Click "Yeni Görev Ekle" in sidebar or top button
2. Select personnel and task location
3. Enter destination and authority
4. Set start date (defaults to current time)
5. Optionally select vehicle and set end date
6. Add description if needed
7. Click "Kaydet" (Save)

### Completing a Task
1. Go to draft tasks list
2. Click edit button on task
3. Change status to "Tamamlandı"
4. Update end date if needed
5. Click "Kaydet" (Save)

### Finding a Task
1. Use text search for quick lookup
2. Or use filters for specific criteria
3. Or browse by date range
4. Or check specific list (draft/completed/archived)

### Deleting a Task
1. Go to draft tasks list
2. Click delete button (trash icon)
3. Confirm in modal dialog
4. Task is soft deleted (hidden)

## Troubleshooting

**Problem:** Can't see add/edit/delete buttons  
**Solution:** You need admin privileges (yonetici = True)

**Problem:** Can't see other users' tasks  
**Solution:** Regular users only see their own tasks

**Problem:** Task not appearing in list  
**Solution:** Check if it's in the correct list (draft/completed/archived)

**Problem:** Can't delete completed task  
**Solution:** Delete button only available for draft tasks

**Problem:** Date validation error  
**Solution:** Ensure end date is after start date

## Technical Details

### Database Fields
- `id` - Auto-increment primary key
- `sofor` - Foreign key to Personel
- `yurt` - Foreign key to GorevYeri
- `varisyeri` - Destination text
- `arac` - Foreign key to Arac (optional)
- `bstarih` - Start datetime
- `bttarih` - End datetime (optional)
- `yetkili` - Authority text
- `ilolur` - Province approval (optional)
- `aciklama` - Description (optional)
- `gizle` - Hidden flag (soft delete)
- `durum` - Status (NULL=draft, 1=completed)
- `aktarildi` - Transfer flag

### Query Optimization
- Uses `select_related()` for foreign keys
- Indexed fields for fast filtering
- Pagination limits result sets
- Efficient date range queries

---

**For technical support or questions, contact your system administrator.**
