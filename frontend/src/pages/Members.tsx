import { useEffect, useState, useRef } from "react";
import { MoreVertical, Plus, Search, Upload, Edit, Trash2 } from "lucide-react";
import { useSearchParams } from "react-router-dom";
import { DashboardLayout } from "@/components/layout/DashboardLayout";
import { toast } from "@/hooks/use-toast";
import { apiFetch } from "@/lib/apiClient";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
} from "@/components/ui/alert-dialog";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Button } from "@/components/ui/button";

interface Member {
  id: string;
  creationDate: string;
  firstName: string;
  lastName: string;
  mobileNumber: string;
  tier: string;
  pointsBalance: number;
  status: "active" | "inactive";
}

interface CreateMemberFormData {
  firstName: string;
  lastName: string;
  email: string;
  mobileNumber: string;
  tier: string;
}

export default function Members() {
  const API_BASE = import.meta.env.VITE_API_BASE_URL;
  const [searchParams] = useSearchParams();
  const [membersData, setMembersData] = useState<Member[]>([]);
  const [totalMembers, setTotalMembers] = useState(0);
  const [page, setPage] = useState(1);
  const [pageSize, setPageSize] = useState(50);
  const [isDialogOpen, setIsDialogOpen] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [isFetching, setIsFetching] = useState(true);
  const [searchQuery, setSearchQuery] = useState(searchParams.get("search") || "");
  const [formData, setFormData] = useState<CreateMemberFormData>({
    firstName: "",
    lastName: "",
    email: "",
    mobileNumber: "",
    tier: "Bronze",
  });
  const [errors, setErrors] = useState<Partial<CreateMemberFormData>>({});
  const [isUploading, setIsUploading] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);
  const [editingMember, setEditingMember] = useState<Member | null>(null);
  const [isDeleteDialogOpen, setIsDeleteDialogOpen] = useState(false);
  const [memberToDelete, setMemberToDelete] = useState<Member | null>(null);

  const fetchMembers = async () => {
    try {
      setIsFetching(true);
      const offset = (page - 1) * pageSize;
      const search = searchQuery.trim();
      const searchParam = search ? `&search=${encodeURIComponent(search)}` : "";
      const res = await apiFetch(
        `${API_BASE}/api/v1/members?limit=${pageSize}&offset=${offset}${searchParam}`
      );
      const payload = await res.json();
      const items = Array.isArray(payload) ? payload : payload.items || [];
      const total = Array.isArray(payload) ? items.length : payload.total ?? items.length;

      const normalized: Member[] = items.map((m: any) => ({
        id: m.id,
        creationDate: m.created_at,
        firstName: m.first_name,
        lastName: m.last_name,
        mobileNumber: m.mobile || "",
        tier: m.tier,
        pointsBalance: m.points_balance,
        status: m.status,
      }));

      setMembersData(normalized);
      setTotalMembers(total);
    } catch (error) {
      console.error("Failed to fetch members:", error);
      toast({
        title: "Error",
        description: "Failed to fetch members",
        variant: "destructive",
      });
    } finally {
      setIsFetching(false);
    }
  };

  useEffect(() => {
    fetchMembers();
  }, [API_BASE, page, pageSize, searchQuery]);

  useEffect(() => {
    setPage(1);
  }, [searchQuery, pageSize]);

  const validateForm = (): boolean => {
    const newErrors: Partial<CreateMemberFormData> = {};

    if (!formData.firstName.trim()) {
      newErrors.firstName = "First name is required";
    }
    if (!formData.lastName.trim()) {
      newErrors.lastName = "Last name is required";
    }
    if (formData.email && !isValidEmail(formData.email)) {
      newErrors.email = "Invalid email format";
    }
    if (formData.mobileNumber && !isValidPhone(formData.mobileNumber)) {
      newErrors.mobileNumber = "Invalid phone format";
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const isValidEmail = (email: string): boolean => {
    return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email);
  };

  const isValidPhone = (phone: string): boolean => {
    return /^[\d\s+()-]+$/.test(phone) && phone.replace(/\D/g, "").length >= 10;
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!validateForm()) {
      return;
    }

    setIsLoading(true);

    try {
      const memberData = {
        first_name: formData.firstName,
        last_name: formData.lastName,
        email: formData.email || null,
        mobile: formData.mobileNumber || null,
        tier: formData.tier,
      };

      const isEditing = !!editingMember;
      const url = isEditing
        ? `${API_BASE}/api/v1/members/${editingMember.id}`
        : `${API_BASE}/api/v1/members`;

      const method = isEditing ? "PUT" : "POST";

      const res = await apiFetch(url, {
        method,
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(memberData),
      });

      if (!res.ok) {
        const errorData = await res.json();
        throw new Error(errorData.detail || `Failed to ${isEditing ? 'update' : 'create'} member`);
      }

      toast({
        title: "Success",
        description: `Member ${formData.firstName} ${formData.lastName} ${isEditing ? 'updated' : 'created'} successfully!`,
      });

      setIsDialogOpen(false);
      setEditingMember(null);
      setFormData({
        firstName: "",
        lastName: "",
        email: "",
        mobileNumber: "",
        tier: "Bronze",
      });
      setErrors({});

      // Refresh members list
      await fetchMembers();
    } catch (error) {
      console.error(`Failed to ${editingMember ? 'update' : 'create'} member:`, error);
      toast({
        title: "Error",
        description: error instanceof Error ? error.message : `Failed to ${editingMember ? 'update' : 'create'} member`,
        variant: "destructive",
      });
    } finally {
      setIsLoading(false);
    }
  };

  const handleAddNew = () => {
    setEditingMember(null);
    setFormData({
      firstName: "",
      lastName: "",
      email: "",
      mobileNumber: "",
      tier: "Bronze",
    });
    setErrors({});
    setIsDialogOpen(true);
  };

  const handleEdit = (member: Member) => {
    setEditingMember(member);
    setFormData({
      firstName: member.firstName,
      lastName: member.lastName,
      email: "",
      mobileNumber: member.mobileNumber,
      tier: member.tier,
    });
    setErrors({});
    setIsDialogOpen(true);
  };

  const handleDelete = (member: Member) => {
    setMemberToDelete(member);
    setIsDeleteDialogOpen(true);
  };

  const confirmDelete = async () => {
    if (!memberToDelete) return;

    setIsLoading(true);

    try {
      const res = await apiFetch(`${API_BASE}/api/v1/members/${memberToDelete.id}`, {
        method: "DELETE",
      });

      if (!res.ok) {
        const errorData = await res.json();
        throw new Error(errorData.detail || "Failed to delete member");
      }

      toast({
        title: "Success",
        description: `Member ${memberToDelete.firstName} ${memberToDelete.lastName} deleted successfully!`,
      });

      setIsDeleteDialogOpen(false);
      setMemberToDelete(null);

      // Refresh members list
      await fetchMembers();
    } catch (error) {
      console.error("Failed to delete member:", error);
      toast({
        title: "Error",
        description: error instanceof Error ? error.message : "Failed to delete member",
        variant: "destructive",
      });
    } finally {
      setIsLoading(false);
    }
  };

  const handleCSVUpload = async (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (!file) return;

    if (!file.name.endsWith('.csv')) {
      toast({
        title: "Invalid File",
        description: "Please upload a CSV file",
        variant: "destructive",
      });
      return;
    }

    setIsUploading(true);

    try {
      const formData = new FormData();
      formData.append('file', file);

      const res = await apiFetch(`${API_BASE}/api/v1/members/bulk`, {
        method: "POST",
        body: formData,
      });

      if (!res.ok) {
        const errorData = await res.json();
        throw new Error(errorData.detail || "Failed to upload CSV");
      }

      const result = await res.json();

      toast({
        title: "Bulk Import Completed",
        description: `${result.created} members imported successfully. ${result.failed} failed.`,
        variant: result.failed > 0 ? "default" : "default",
      });

      // Refresh members list
      await fetchMembers();
    } catch (error) {
      console.error("CSV upload error:", error);
      toast({
        title: "Upload Failed",
        description: error instanceof Error ? error.message : "Failed to upload CSV",
        variant: "destructive",
      });
    } finally {
      setIsUploading(false);
      // Reset file input
      if (fileInputRef.current) {
        fileInputRef.current.value = '';
      }
    }
  };

  const handleInputChange = (field: keyof CreateMemberFormData, value: string) => {
    setFormData((prev) => ({
      ...prev,
      [field]: value,
    }));
    // Clear error for this field when user starts typing
    if (errors[field]) {
      setErrors((prev) => ({
        ...prev,
        [field]: undefined,
      }));
    }
  };

  return (
    <DashboardLayout breadcrumbs={[{ label: "Home", href: "/" }, { label: "Loyalty", href: "/" }, { label: "Members" }]}>
      {/* Page Header */}
      <div className="flex items-center justify-between mb-6">
        <h1 className="page-title">Members ({totalMembers})</h1>
        <div className="flex items-center gap-2">
          <input
            ref={fileInputRef}
            type="file"
            accept=".csv"
            onChange={handleCSVUpload}
            className="hidden"
          />
          <button
            onClick={() => fileInputRef.current?.click()}
            disabled={isUploading}
            className="px-4 py-2 bg-blue-600 text-white rounded-lg text-sm font-medium flex items-center gap-2 hover:bg-blue-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
          >
            <Upload className="w-4 h-4" />
            {isUploading ? "Uploading..." : "Import CSV"}
          </button>
          <button
            onClick={handleAddNew}
            className="px-4 py-2 bg-foreground text-background rounded-lg text-sm font-medium flex items-center gap-2 hover:bg-foreground/90 transition-colors"
          >
            <Plus className="w-4 h-4" />
            Add new
          </button>
        </div>
      </div>

      {/* Search Bar */}
      <div className="mb-4">
        <div className="relative w-full max-w-md">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-muted-foreground" />
          <Input
            type="text"
            placeholder="Search by name, mobile, tier, or ID..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="pl-10"
          />
        </div>
      </div>

      {/* Data Table */}
      <div className="bg-card rounded-lg border border-border overflow-hidden">
        {isFetching ? (
          <div className="flex items-center justify-center py-12">
            <div className="text-muted-foreground">Loading members...</div>
          </div>
        ) : membersData.length === 0 ? (
          <div className="flex items-center justify-center py-12">
            <div className="text-center">
              <p className="text-muted-foreground">
                {searchQuery ? "No members found matching your search" : "No members yet"}
              </p>
              {!searchQuery && (
                <button
                  onClick={handleAddNew}
                  className="mt-4 text-sm text-primary hover:underline"
                >
                  Add your first member
                </button>
              )}
            </div>
          </div>
        ) : (
          <table className="data-table">
            <thead>
              <tr className="bg-muted/30">
                <th>Creation date</th>
                <th>Firstname</th>
                <th>Lastname</th>
                <th>Mobile number</th>
                <th>Tier</th>
                <th>Points Balance</th>
                <th>Status</th>
                <th></th>
              </tr>
            </thead>
            <tbody>
              {membersData.map((member) => (
                <tr key={member.id}>
                  <td className="text-muted-foreground">{member.creationDate}</td>
                  <td className="font-medium text-foreground">{member.firstName}</td>
                  <td className="text-foreground">{member.lastName}</td>
                  <td className="text-foreground">{member.mobileNumber}</td>
                  <td>
                    <span className="badge-gold">{member.tier}</span>
                  </td>
                  <td className="font-medium text-foreground">{member.pointsBalance}</td>
                  <td>
                    <span
                      className={`w-2 h-2 rounded-full inline-block ${
                        member.status === "active"
                          ? "bg-emerald-500"
                          : "bg-gray-300"
                      }`}
                    ></span>
                  </td>
                  <td>
                    <DropdownMenu>
                      <DropdownMenuTrigger asChild>
                        <button className="p-1 hover:bg-muted rounded transition-colors">
                          <MoreVertical className="w-4 h-4 text-muted-foreground" />
                        </button>
                      </DropdownMenuTrigger>
                      <DropdownMenuContent align="end">
                        <DropdownMenuItem onClick={() => handleEdit(member)}>
                          <Edit className="w-4 h-4 mr-2" />
                          Edit Member
                        </DropdownMenuItem>
                        <DropdownMenuItem
                          onClick={() => handleDelete(member)}
                          className="text-red-600 focus:text-red-600"
                        >
                          <Trash2 className="w-4 h-4 mr-2" />
                          Delete Member
                        </DropdownMenuItem>
                      </DropdownMenuContent>
                    </DropdownMenu>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>

      <div className="flex flex-wrap items-center justify-between gap-3 mt-4 text-sm text-muted-foreground">
        <div>
          {totalMembers > 0
            ? `Showing ${(page - 1) * pageSize + 1}-${Math.min(
                page * pageSize,
                totalMembers
              )} of ${totalMembers}`
            : "No members to show"}
        </div>
        <div className="flex items-center gap-2">
          <span>Rows</span>
          <Select value={String(pageSize)} onValueChange={(value) => setPageSize(Number(value))}>
            <SelectTrigger className="h-8 w-[90px]">
              <SelectValue />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="25">25</SelectItem>
              <SelectItem value="50">50</SelectItem>
              <SelectItem value="100">100</SelectItem>
            </SelectContent>
          </Select>
          <Button
            variant="outline"
            size="sm"
            onClick={() => setPage((prev) => Math.max(1, prev - 1))}
            disabled={page <= 1}
          >
            Previous
          </Button>
          <span>
            Page {page} of {Math.max(1, Math.ceil(totalMembers / pageSize))}
          </span>
          <Button
            variant="outline"
            size="sm"
            onClick={() => setPage((prev) => prev + 1)}
            disabled={page >= Math.max(1, Math.ceil(totalMembers / pageSize))}
          >
            Next
          </Button>
        </div>
      </div>

      {/* Add/Edit Member Dialog */}
      <Dialog open={isDialogOpen} onOpenChange={setIsDialogOpen}>
        <DialogContent className="sm:max-w-[500px]">
          <DialogHeader>
            <DialogTitle>{editingMember ? "Edit Member" : "Add New Member"}</DialogTitle>
            <DialogDescription>
              {editingMember
                ? "Update member information. Required fields are marked with an asterisk."
                : "Create a new loyalty program member. Required fields are marked with an asterisk."}
            </DialogDescription>
          </DialogHeader>
          <form onSubmit={handleSubmit} className="space-y-4">
            {/* First Name */}
            <div className="space-y-2">
              <Label htmlFor="firstName" className="required">
                First Name *
              </Label>
              <Input
                id="firstName"
                placeholder="Enter first name"
                value={formData.firstName}
                onChange={(e) => handleInputChange("firstName", e.target.value)}
                disabled={isLoading}
                className={errors.firstName ? "border-red-500" : ""}
              />
              {errors.firstName && (
                <p className="text-sm text-red-500">{errors.firstName}</p>
              )}
            </div>

            {/* Last Name */}
            <div className="space-y-2">
              <Label htmlFor="lastName" className="required">
                Last Name *
              </Label>
              <Input
                id="lastName"
                placeholder="Enter last name"
                value={formData.lastName}
                onChange={(e) => handleInputChange("lastName", e.target.value)}
                disabled={isLoading}
                className={errors.lastName ? "border-red-500" : ""}
              />
              {errors.lastName && (
                <p className="text-sm text-red-500">{errors.lastName}</p>
              )}
            </div>

            {/* Email */}
            <div className="space-y-2">
              <Label htmlFor="email">Email Address</Label>
              <Input
                id="email"
                type="email"
                placeholder="Enter email address"
                value={formData.email}
                onChange={(e) => handleInputChange("email", e.target.value)}
                disabled={isLoading}
                className={errors.email ? "border-red-500" : ""}
              />
              {errors.email && (
                <p className="text-sm text-red-500">{errors.email}</p>
              )}
            </div>

            {/* Mobile Number */}
            <div className="space-y-2">
              <Label htmlFor="mobileNumber">Mobile Number</Label>
              <Input
                id="mobileNumber"
                placeholder="Enter mobile number"
                value={formData.mobileNumber}
                onChange={(e) => handleInputChange("mobileNumber", e.target.value)}
                disabled={isLoading}
                className={errors.mobileNumber ? "border-red-500" : ""}
              />
              {errors.mobileNumber && (
                <p className="text-sm text-red-500">{errors.mobileNumber}</p>
              )}
            </div>

            {/* Tier */}
            <div className="space-y-2">
              <Label htmlFor="tier">Membership Tier</Label>
              <Select value={formData.tier} onValueChange={(value) => handleInputChange("tier", value)} disabled={isLoading}>
                <SelectTrigger id="tier">
                  <SelectValue placeholder="Select tier" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="Bronze">Bronze</SelectItem>
                  <SelectItem value="Silver">Silver</SelectItem>
                  <SelectItem value="Gold">Gold</SelectItem>
                  <SelectItem value="Platinum">Platinum</SelectItem>
                </SelectContent>
              </Select>
            </div>

            <DialogFooter>
              <Button
                type="button"
                variant="outline"
                onClick={() => setIsDialogOpen(false)}
                disabled={isLoading}
              >
                Cancel
              </Button>
              <Button type="submit" disabled={isLoading}>
                {isLoading
                  ? editingMember ? "Updating..." : "Creating..."
                  : editingMember ? "Update Member" : "Create Member"}
              </Button>
            </DialogFooter>
          </form>
        </DialogContent>
      </Dialog>

      {/* Delete Confirmation Dialog */}
      <AlertDialog open={isDeleteDialogOpen} onOpenChange={setIsDeleteDialogOpen}>
        <AlertDialogContent>
          <AlertDialogHeader>
            <AlertDialogTitle>Delete Member</AlertDialogTitle>
            <AlertDialogDescription>
              Are you sure you want to delete <strong>{memberToDelete?.firstName} {memberToDelete?.lastName}</strong>?
              This action cannot be undone. All associated data including transaction history will be preserved but the member will be removed.
            </AlertDialogDescription>
          </AlertDialogHeader>
          <AlertDialogFooter>
            <AlertDialogCancel disabled={isLoading}>Cancel</AlertDialogCancel>
            <AlertDialogAction
              onClick={confirmDelete}
              disabled={isLoading}
              className="bg-red-600 hover:bg-red-700"
            >
              {isLoading ? "Deleting..." : "Delete Member"}
            </AlertDialogAction>
          </AlertDialogFooter>
        </AlertDialogContent>
      </AlertDialog>
    </DashboardLayout>
  );
}