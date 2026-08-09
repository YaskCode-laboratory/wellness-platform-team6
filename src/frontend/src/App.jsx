import React, { useState, useEffect, useRef } from 'react';
import { 
  Dumbbell, 
  MessageSquare, 
  TrendingUp, 
  User, 
  Check, 
  Send, 
  RotateCcw, 
  Sparkles, 
  Flame, 
  Activity, 
  CheckCircle,
  AlertTriangle,
  Lock,
  Mail,
  Calendar,
  LogOut,
  ChevronRight,
  ShieldCheck,
  Users,
  Building,
  FileText,
  HeartPulse,
  ArrowRightLeft,
  XCircle,
  Plus,
  Stethoscope,
  Power,
  Search,
  Eye,
  Award,
  Edit3,
  Trash2,
  Play,
  Key,
  UserCheck
} from 'lucide-react';

const API_URL = import.meta.env.VITE_API_URL || 'http://127.0.0.1:8001';

const COMMON_HEALTH_CONDITIONS = [
  "Hernia Discal L4-L5 / Lumbar",
  "Lesión de Rodilla (Menisco / Ligamento)",
  "Hipertensión Arterial",
  "Escoliosis",
  "Asma / Limitación Respiratoria",
  "Molestia en Hombro (Manguito Rotador)"
];

function App() {
  // ─── ESTADOS DE CONECTIVIDAD Y SESIÓN MULTI-ROL ───
  const [isOnline, setIsOnline] = useState(false);
  const [checkingStatus, setCheckingStatus] = useState(true);
  const [userId, setUserId] = useState(localStorage.getItem('wellness_userId') || '');
  const [userEmail, setUserEmail] = useState(localStorage.getItem('wellness_userEmail') || '');
  const [userName, setUserName] = useState(localStorage.getItem('wellness_userName') || '');
  const [userRole, setUserRole] = useState(localStorage.getItem('wellness_userRole') || 'athlete');
  const [gymBranchId, setGymBranchId] = useState(localStorage.getItem('wellness_gymBranchId') || 'branch_central');
  const [assignedCoachId, setAssignedCoachId] = useState(localStorage.getItem('wellness_assignedCoachId') || 'coach_carlos');
  const [isAuthenticated, setIsAuthenticated] = useState(!!localStorage.getItem('wellness_userId'));

  // ─── ESTADOS DE AUTENTICACIÓN ESTRICTA & REGISTRO PÚBLICO DE CLIENTES ───
  const [authMode, setAuthMode] = useState('login'); // 'login' o 'register'
  const [authEmail, setAuthEmail] = useState('');
  const [authPassword, setAuthPassword] = useState('');
  const [authName, setAuthName] = useState('');
  const [authBranch, setAuthBranch] = useState('branch_central'); // Sucursal seleccionada por el cliente al registrarse
  const [authHealth, setAuthHealth] = useState([]);
  const [authTrainingDays, setAuthTrainingDays] = useState(['Lunes', 'Miércoles', 'Viernes']);
  const [authError, setAuthError] = useState('');

  // ─── NAVEGACIÓN Y TABS POR ROL ───
  const [currentTab, setCurrentTab] = useState(userRole === 'admin' ? 'usuarios' : userRole === 'coach' ? 'atletas' : 'entrenar');
  const [loading, setLoading] = useState(false);
  const [toast, setToast] = useState(null);

  // ─── ESTADOS DE DATOS PÚBLICOS Y PRIVADOS ───
  const [profile, setProfile] = useState(null);
  const [routine, setRoutine] = useState(null);
  const [sessions, setSessions] = useState([]);
  const [activeSession, setActiveSession] = useState(null);
  const [healthConditions, setHealthConditions] = useState([]);

  // ─── ESTADOS DEL ADMIN DE GIMNASIO ───
  const [adminUsers, setAdminUsers] = useState([]);
  const [userSearchQuery, setUserSearchQuery] = useState('');
  const [roleFilter, setRoleFilter] = useState('todos');
  const [branches, setBranches] = useState([]);
  const [coaches, setCoaches] = useState([]);
  const [newBranchName, setNewBranchName] = useState('');
  const [newBranchCity, setNewBranchCity] = useState('');
  const [newBranchAddress, setNewBranchAddress] = useState('');
  
  // Modal Reasignación de Coach para Atletas
  const [reassigningAthlete, setReassigningAthlete] = useState(null);
  const [targetNewCoachId, setTargetNewCoachId] = useState('coach_carlos');

  // Alta de Personal (Coach o Admin)
  const [newStaffRole, setNewStaffRole] = useState('coach');
  const [newStaffEmail, setNewStaffEmail] = useState('');
  const [newStaffPassword, setNewStaffPassword] = useState('');
  const [newStaffName, setNewStaffName] = useState('');
  const [newStaffSpecialty, setNewStaffSpecialty] = useState('Levantamiento de Pesas e Hipertrofia');
  const [newStaffBranch, setNewStaffBranch] = useState('branch_central');

  // Modal Edición Completa por el Admin
  const [editingUserForAdmin, setEditingUserForAdmin] = useState(null);
  const [editName, setEditName] = useState('');
  const [editEmail, setEditEmail] = useState('');
  const [editNewPassword, setEditNewPassword] = useState('');
  const [editRole, setEditRole] = useState('athlete');
  const [editBranch, setEditBranch] = useState('branch_central');
  const [editCoach, setEditCoach] = useState('coach_carlos');
  const [editGoal, setEditGoal] = useState('hipertrofia');
  const [editHealth, setEditHealth] = useState([]);

  // ─── ESTADOS DEL ENTRENADOR (COACH) ───
  const [coachAthletes, setCoachAthletes] = useState([]);
  const [coachPendingRequests, setCoachPendingRequests] = useState([]);
  const [coachFeedbackInput, setCoachFeedbackInput] = useState('');
  const [selectedTechnicalFile, setSelectedTechnicalFile] = useState(null);

  // Modal Edición de Rutina por el Coach
  const [editingRoutineAthlete, setEditingRoutineAthlete] = useState(null);
  const [customRoutineSchedule, setCustomRoutineSchedule] = useState([]);
  const [customRoutineFocus, setCustomRoutineFocus] = useState('');

  // ─── ESTADOS DE ATLETA (SOLICITUD DE RUTINA) ───
  const [athleteRequests, setAthleteRequests] = useState([]);
  const [showRequestModal, setShowRequestModal] = useState(false);
  const [reqDays, setReqDays] = useState(['Lunes', 'Miércoles', 'Viernes']);
  const [reqGoal, setReqGoal] = useState('hipertrofia');
  const [reqNotes, setReqNotes] = useState('');

  // ─── CHATBOT IA ───
  const [chatMessages, setChatMessages] = useState([
    { 
      sender: 'agent', 
      text: '¡Hola! Soy tu Wellness Coach IA. Estoy listo para ayudarte con biomecánica, alternativas de ejercicios por lesiones o sobrecarga progresiva. ¿Qué entrenas hoy?' 
    }
  ]);
  const [chatInput, setChatInput] = useState('');
  const chatEndRef = useRef(null);

  // ─── CARGAR SUCURSALES Y VERIFICAR CONEXIÓN AL INICIAR ───
  useEffect(() => {
    async function checkBackend() {
      try {
        const res = await fetch(`${API_URL}/`);
        if (res.ok) {
          setIsOnline(true);
          // Cargar sucursales para el selector público de registro
          const bRes = await fetch(`${API_URL}/api/v1/branches`);
          if (bRes.ok) {
            const bData = await bRes.json();
            setBranches(bData);
          }
          const cRes = await fetch(`${API_URL}/api/v1/coaches`);
          if (cRes.ok) {
            const cData = await cRes.json();
            setCoaches(cData);
          }

          if (isAuthenticated && userId) {
            await fetchCloudData(userId, userRole);
          } else {
            setCheckingStatus(false);
          }
        } else {
          setCheckingStatus(false);
        }
      } catch (err) {
        setIsOnline(false);
        setCheckingStatus(false);
      }
    }
    checkBackend();
  }, [isAuthenticated, userId, userRole]);

  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [chatMessages]);

  const showToast = (msg) => {
    setToast(msg);
    setTimeout(() => setToast(null), 4000);
  };

  // ─── CARGAR DATOS DESDE EL BACKEND EN LA NUBE ───
  const fetchCloudData = async (uid, role) => {
    setLoading(true);
    try {
      if (role === 'athlete') {
        const uRes = await fetch(`${API_URL}/api/v1/users/${uid}`);
        if (uRes.ok) {
          const uData = await uRes.json();
          setProfile(uData);
          setHealthConditions(uData.fitness_profile?.health_conditions || []);
        }

        const rRes = await fetch(`${API_URL}/api/v1/ai/routine/${uid}`);
        if (rRes.ok) {
          const rData = await rRes.json();
          setRoutine(rData);
        }

        const sRes = await fetch(`${API_URL}/api/v1/sessions/${uid}`);
        if (sRes.ok) {
          const sData = await sRes.json();
          setSessions(sData);
        }

        const reqRes = await fetch(`${API_URL}/api/v1/athlete/routine-requests/${uid}`);
        if (reqRes.ok) {
          const reqData = await reqRes.json();
          setAthleteRequests(reqData);
        }
      } else if (role === 'coach') {
        const athRes = await fetch(`${API_URL}/api/v1/coach/${uid}/athletes`);
        if (athRes.ok) {
          const athData = await athRes.json();
          setCoachAthletes(athData);
        }

        const reqRes = await fetch(`${API_URL}/api/v1/coach/${uid}/requests`);
        if (reqRes.ok) {
          const reqData = await reqRes.json();
          setCoachPendingRequests(reqData);
        }
      } else if (role === 'admin') {
        const usersRes = await fetch(`${API_URL}/api/v1/admin/users`);
        if (usersRes.ok) {
          const uData = await usersRes.json();
          setAdminUsers(uData);
        }

        const bRes = await fetch(`${API_URL}/api/v1/branches`);
        if (bRes.ok) {
          const bData = await bRes.json();
          setBranches(bData);
        }

        const cRes = await fetch(`${API_URL}/api/v1/coaches`);
        if (cRes.ok) {
          const cData = await cRes.json();
          setCoaches(cData);
        }
      }
    } catch (err) {
      console.error("Error al cargar datos:", err);
    } finally {
      setLoading(false);
      setCheckingStatus(false);
    }
  };

  // ─── ADMIN: REASIGNAR / TRANSFERIR ATLETA A OTRO COACH ───
  const handleReassignAthleteCoach = async (e) => {
    e.preventDefault();
    if (!reassigningAthlete) return;
    setLoading(true);

    try {
      const res = await fetch(`${API_URL}/api/v1/admin/reassign-athlete`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          athlete_id: reassigningAthlete.user_id,
          new_coach_id: targetNewCoachId
        })
      });

      if (res.ok) {
        showToast(`✅ Atleta ${reassigningAthlete.name} reasignado exitosamente al nuevo Coach.`);
        setReassigningAthlete(null);
        await fetchCloudData(userId, userRole);
      } else {
        showToast("Error al reasignar entrenador.");
      }
    } catch (err) {
      showToast("Error de conexión al reasignar coach.");
    } finally {
      setLoading(false);
    }
  };

  // ─── ADMIN: GUARDAR EDICIÓN COMPLETA DE USUARIO Y RECTIFICACIÓN DE CONTRASEÑA ───
  const handleSaveAdminUserEdit = async (e) => {
    e.preventDefault();
    if (!editingUserForAdmin) return;
    setLoading(true);

    try {
      const res = await fetch(`${API_URL}/api/v1/admin/users/${editingUserForAdmin.user_id}/update`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          name: editName,
          email: editEmail,
          new_password: editNewPassword || null,
          role: editRole,
          gym_branch_id: editBranch,
          assigned_coach_id: editCoach,
          goal: editGoal,
          health_conditions: editHealth,
          training_days: editingUserForAdmin.training_days || ["Lunes", "Miércoles", "Viernes"]
        })
      });

      if (res.ok) {
        showToast("✅ Datos del usuario y credenciales actualizados por el Administrador.");
        setEditingUserForAdmin(null);
        setEditNewPassword('');
        await fetchCloudData(userId, userRole);
      }
    } catch (err) {
      showToast("Error al guardar cambios de usuario.");
    } finally {
      setLoading(false);
    }
  };

  const openAdminUserEditModal = (u) => {
    setEditingUserForAdmin(u);
    setEditName(u.name);
    setEditEmail(u.email);
    setEditNewPassword('');
    setEditRole(u.role);
    setEditBranch(u.gym_branch_id);
    setEditCoach(u.assigned_coach_id || 'coach_carlos');
    setEditGoal(u.goal || 'hipertrofia');
    setEditHealth(u.health_conditions || []);
  };

  // ─── COACH: GUARDAR RUTINA PERSONALIZADA PARA UN ATLETA ───
  const handleOpenCoachRoutineEditor = async (ath) => {
    setLoading(true);
    try {
      const res = await fetch(`${API_URL}/api/v1/ai/routine/${ath.user_id}`);
      if (res.ok) {
        const rData = await res.json();
        setEditingRoutineAthlete(ath);
        setCustomRoutineFocus(rData.focus || `Rutina Personalizada por ${userName}`);
        setCustomRoutineSchedule(rData.weekly_schedule || []);
      }
    } catch (err) {
      showToast("Error al abrir editor de rutina.");
    } finally {
      setLoading(false);
    }
  };

  const handleSaveCoachCustomRoutine = async (e) => {
    e.preventDefault();
    if (!editingRoutineAthlete) return;
    setLoading(true);

    try {
      const res = await fetch(`${API_URL}/api/v1/coach/routine/${editingRoutineAthlete.user_id}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          focus: customRoutineFocus,
          weekly_schedule: customRoutineSchedule
        })
      });

      if (res.ok) {
        showToast(`✏️ ¡Rutina personalizada guardada para ${editingRoutineAthlete.personal_info?.name}!`);
        setEditingRoutineAthlete(null);
      }
    } catch (err) {
      showToast("Error al guardar rutina del coach.");
    } finally {
      setLoading(false);
    }
  };

  // ─── ADMIN: ACTIVAR / INACTIVAR USUARIO ───
  const handleToggleUserStatus = async (targetUserId, currentStatus) => {
    setLoading(true);
    try {
      const res = await fetch(`${API_URL}/api/v1/admin/users/${targetUserId}/status`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ is_active: !currentStatus })
      });
      if (res.ok) {
        showToast(!currentStatus ? "✅ Cuenta activada correctamente." : "⏸️ Cuenta inhabilitada.");
        await fetchCloudData(userId, userRole);
      }
    } catch (err) {
      showToast("Error al cambiar estado del usuario.");
    } finally {
      setLoading(false);
    }
  };

  // ─── COACH / ADMIN: CARGAR FICHA TÉCNICA GARANTIZADA ───
  const handleOpenTechnicalFile = async (targetUserId) => {
    setLoading(true);
    try {
      const res = await fetch(`${API_URL}/api/v1/athlete/${targetUserId}/technical-file`);
      if (res.ok) {
        const fileData = await res.json();
        setSelectedTechnicalFile(fileData);
      } else {
        showToast("No se pudo obtener el expediente del usuario.");
      }
    } catch (err) {
      showToast("Error de conexión al cargar la ficha.");
    } finally {
      setLoading(false);
    }
  };

  // ─── AUTENTICACIÓN: LOGIN REAL ───
  const handleLoginSubmit = async (e) => {
    e.preventDefault();
    setAuthError('');
    if (!authEmail || !authPassword) {
      setAuthError("Por favor ingrese correo y contraseña.");
      return;
    }

    setLoading(true);
    try {
      const res = await fetch(`${API_URL}/api/v1/auth/login`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email: authEmail, password: authPassword })
      });

      if (res.ok) {
        const data = await res.json();
        setUserId(data.user_id);
        setUserEmail(authEmail);
        setUserName(data.name);
        setUserRole(data.role);
        setGymBranchId(data.gym_branch_id);
        setAssignedCoachId(data.assigned_coach_id || 'coach_carlos');
        setIsAuthenticated(true);

        localStorage.setItem('wellness_userId', data.user_id);
        localStorage.setItem('wellness_userEmail', authEmail);
        localStorage.setItem('wellness_userName', data.name);
        localStorage.setItem('wellness_userRole', data.role);
        localStorage.setItem('wellness_gymBranchId', data.gym_branch_id);

        if (data.role === 'admin') setCurrentTab('usuarios');
        else if (data.role === 'coach') setCurrentTab('atletas');
        else setCurrentTab('entrenar');

        showToast(`¡Bienvenido, ${data.name}! Sesión iniciada correctamente.`);
        await fetchCloudData(data.user_id, data.role);
      } else {
        const errData = await res.json();
        setAuthError(errData.detail || "Error al iniciar sesión.");
      }
    } catch (err) {
      setAuthError("No se pudo conectar con el servidor backend.");
    } finally {
      setLoading(false);
    }
  };

  // ─── AUTENTICACIÓN: REGISTRO PÚBLICO DE CLIENTES CON SELECCIÓN DE SUCURSAL ───
  const handleRegisterSubmit = async (e) => {
    e.preventDefault();
    setAuthError('');
    if (!authEmail || !authPassword || !authName) {
      setAuthError("Por favor complete los campos obligatorios.");
      return;
    }

    setLoading(true);
    try {
      const res = await fetch(`${API_URL}/api/v1/auth/register`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          email: authEmail,
          password: authPassword,
          name: authName,
          role: 'athlete', // Exclusivo clientes
          gym_branch_id: authBranch, // Sucursal seleccionada por el cliente
          assigned_coach_id: 'coach_carlos',
          age: 25,
          weight: 70.0,
          height: 170.0,
          goal: 'hipertrofia',
          level: 'basico',
          health_conditions: authHealth,
          training_days: authTrainingDays
        })
      });

      if (res.ok) {
        const data = await res.json();
        setUserId(data.user_id);
        setUserEmail(authEmail);
        setUserName(data.name);
        setUserRole(data.role);
        setIsAuthenticated(true);

        localStorage.setItem('wellness_userId', data.user_id);
        localStorage.setItem('wellness_userEmail', authEmail);
        localStorage.setItem('wellness_userName', data.name);
        localStorage.setItem('wellness_userRole', data.role);

        showToast("¡Cuenta de Atleta registrada con éxito en tu sucursal!");
        await fetchCloudData(data.user_id, data.role);
      } else {
        const errData = await res.json();
        setAuthError(errData.detail || "Error al registrar usuario.");
      }
    } catch (err) {
      setAuthError("Error de conexión al servidor.");
    } finally {
      setLoading(false);
    }
  };

  // ─── CIERRE DE SESIÓN SEGURO ───
  const handleLogout = () => {
    localStorage.clear();
    setIsAuthenticated(false);
    setUserId('');
    setUserName('');
    setUserEmail('');
    setUserRole('athlete');
    setProfile(null);
    setRoutine(null);
    setSessions([]);
    setActiveSession(null);
    showToast("Sesión cerrada correctamente.");
  };

  // ─── ATLETA: SOLICITAR CAMBIO DE RUTINA ───
  const handleCreateRoutineRequest = async (e) => {
    e.preventDefault();
    setLoading(true);
    try {
      const res = await fetch(`${API_URL}/api/v1/athlete/routine-request/${userId}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          requested_days: reqDays,
          requested_goal: reqGoal,
          notes: reqNotes
        })
      });
      if (res.ok) {
        showToast("¡Solicitud enviada a tu Coach para su revisión!");
        setShowRequestModal(false);
        setReqNotes('');
        await fetchCloudData(userId, userRole);
      }
    } catch (err) {
      showToast("Error al enviar solicitud.");
    } finally {
      setLoading(false);
    }
  };

  // ─── COACH: APROBAR O RECHAZAR SOLICITUD DE RUTINA ───
  const handleCoachRequestAction = async (requestId, action) => {
    setLoading(true);
    try {
      const res = await fetch(`${API_URL}/api/v1/coach/requests/${requestId}/action`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          action: action,
          feedback: coachFeedbackInput || (action === 'approve' ? 'Solicitud aprobada y rutina adaptada con IA.' : 'Solicitud rechazada.')
        })
      });

      if (res.ok) {
        showToast(action === 'approve' ? "✅ Solicitud APROBADA y rutina regenerada por IA." : "❌ Solicitud rechazada.");
        setCoachFeedbackInput('');
        await fetchCloudData(userId, userRole);
      }
    } catch (err) {
      showToast("Error al procesar solicitud.");
    } finally {
      setLoading(false);
    }
  };

  // ─── ADMIN: CREAR PERSONAL (COACH O ADMIN) ───
  const handleAdminCreateStaff = async (e) => {
    e.preventDefault();
    if (!newStaffEmail || !newStaffPassword || !newStaffName) {
      showToast("Completa los datos del usuario.");
      return;
    }
    setLoading(true);
    try {
      const res = await fetch(`${API_URL}/api/v1/admin/staff`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          email: newStaffEmail,
          password: newStaffPassword,
          name: newStaffName,
          role: newStaffRole,
          gym_branch_id: newStaffBranch,
          specialty: newStaffSpecialty
        })
      });
      if (res.ok) {
        showToast(`¡Usuario ${newStaffRole.toUpperCase()} registrado exitosamente en el Gimnasio!`);
        setNewStaffEmail('');
        setNewStaffPassword('');
        setNewStaffName('');
        await fetchCloudData(userId, userRole);
      } else {
        const err = await res.json();
        showToast(err.detail || "Error al crear usuario.");
      }
    } catch (err) {
      showToast("Error de conexión.");
    } finally {
      setLoading(false);
    }
  };

  // ─── ADMIN: CREAR SUCURSAL ───
  const handleAdminCreateBranch = async (e) => {
    e.preventDefault();
    if (!newBranchName || !newBranchCity) {
      showToast("Completa los datos de la sucursal.");
      return;
    }
    setLoading(true);
    try {
      const res = await fetch(`${API_URL}/api/v1/branches`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          name: newBranchName,
          city: newBranchCity,
          address: newBranchAddress || 'Dirección Principal'
        })
      });
      if (res.ok) {
        showToast("¡Nueva Sucursal del Gimnasio agregada!");
        setNewBranchName('');
        setNewBranchCity('');
        setNewBranchAddress('');
        await fetchCloudData(userId, userRole);
      }
    } catch (err) {
      showToast("Error al crear sucursal.");
    } finally {
      setLoading(false);
    }
  };

  // ─── MODO GYM: SESIÓN DE ENTRENAMIENTO EN VIVO E INTERACTIVA ───
  const startWorkoutSession = (dayPlan) => {
    const exercisesLog = dayPlan.exercises.map(ex => ({
      exercise_id: ex.name.toLowerCase().replace(/\s+/g, '_'),
      exercise_name: ex.name,
      sets: Array.from({ length: ex.sets || 3 }).map((_, i) => ({
        set_number: i + 1,
        weight: 50,
        reps: parseInt(ex.reps) || 10,
        completed: false
      }))
    }));

    setActiveSession({
      date: new Date().toISOString(),
      day_name: dayPlan.day,
      exercises: exercisesLog
    });
    showToast("🔥 ¡Modo Gimnasio activado! Registra tus cargas y repeticiones.");
  };

  const handleUpdateSetWeight = (exIdx, setIdx, newWeight) => {
    const updated = { ...activeSession };
    updated.exercises[exIdx].sets[setIdx].weight = parseFloat(newWeight) || 0;
    setActiveSession(updated);
  };

  const handleUpdateSetReps = (exIdx, setIdx, newReps) => {
    const updated = { ...activeSession };
    updated.exercises[exIdx].sets[setIdx].reps = parseInt(newReps) || 0;
    setActiveSession(updated);
  };

  const handleToggleSetComplete = (exIdx, setIdx) => {
    const updated = { ...activeSession };
    const current = updated.exercises[exIdx].sets[setIdx].completed;
    updated.exercises[exIdx].sets[setIdx].completed = !current;
    setActiveSession(updated);
  };

  const handleAddSetToExercise = (exIdx) => {
    const updated = { ...activeSession };
    const sets = updated.exercises[exIdx].sets;
    const lastSet = sets[sets.length - 1] || { weight: 50, reps: 10 };
    sets.push({
      set_number: sets.length + 1,
      weight: lastSet.weight,
      reps: lastSet.reps,
      completed: false
    });
    setActiveSession(updated);
  };

  const handleFinishWorkout = async () => {
    if (!activeSession) return;
    setLoading(true);
    try {
      const res = await fetch(`${API_URL}/api/v1/sessions/${userId}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          date: activeSession.date,
          exercises: activeSession.exercises
        })
      });
      if (res.ok) {
        showToast("🏆 ¡Entrenamiento guardado con éxito!");
        setActiveSession(null);
        await fetchCloudData(userId, userRole);
      }
    } catch (err) {
      showToast("Entrenamiento finalizado.");
      setActiveSession(null);
    } finally {
      setLoading(false);
    }
  };

  // ─── CHATBOT IA EN VIVO ───
  const handleSendChatMessage = async () => {
    if (!chatInput.trim()) return;
    const textToSend = chatInput;
    setChatMessages(prev => [...prev, { sender: 'user', text: textToSend }]);
    setChatInput('');
    setLoading(true);

    try {
      const res = await fetch(`${API_URL}/api/v1/ai/chat/${userId || 'user123'}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: textToSend })
      });
      if (res.ok) {
        const data = await res.json();
        setChatMessages(prev => [...prev, { sender: 'agent', text: data.response }]);
      } else {
        setChatMessages(prev => [...prev, { sender: 'agent', text: "💪 En el entrenamiento de fuerza, la sobrecarga progresiva y la buena técnica son fundamentales." }]);
      }
    } catch (err) {
      setChatMessages(prev => [...prev, { sender: 'agent', text: "💪 Recuerda mantener un rango de movimiento completo y aplicar sobrecarga progresiva." }]);
    } finally {
      setLoading(false);
    }
  };

  // ─── FILTRADO DEL DIRECTORIO DE USUARIOS PARA ADMIN ───
  const filteredAdminUsers = adminUsers.filter(u => {
    const matchesSearch = u.name?.toLowerCase().includes(userSearchQuery.toLowerCase()) || u.email?.toLowerCase().includes(userSearchQuery.toLowerCase());
    const matchesRole = roleFilter === 'todos' || u.role === roleFilter;
    return matchesSearch && matchesRole;
  });

  // ═════════════════════════════════════════════════════════════
  // PANTALLA 1: AUTENTICACIÓN OBLIGATORIA SI NO HAY SESIÓN ACTIVA
  // ═════════════════════════════════════════════════════════════
  if (!isAuthenticated) {
    return (
      <div className="auth-container-screen">
        <div className="card-glass auth-wrapper">
          <div style={{ textAlign: 'center', marginBottom: '24px' }}>
            <div style={{ width: '60px', height: '60px', borderRadius: '16px', background: 'rgba(16,185,129,0.15)', border: '1px solid rgba(16,185,129,0.3)', display: 'inline-flex', alignItems: 'center', justifyContent: 'center', color: '#10b981', marginBottom: '12px' }}>
              <Dumbbell size={32} />
            </div>
            <h1 className="logo-text" style={{ fontSize: '2rem' }}>Wellness Lift</h1>
            <p style={{ color: 'var(--text-secondary)', fontSize: '0.85rem', marginTop: '4px' }}>Plataforma SaaS Profesional para Gimnasios & IA</p>
          </div>

          {authError && (
            <div style={{ padding: '12px 16px', backgroundColor: 'rgba(239, 68, 68, 0.1)', border: '1px solid rgba(239, 68, 68, 0.3)', borderRadius: '12px', color: '#f87171', fontSize: '0.85rem', marginBottom: '20px', display: 'flex', alignItems: 'center', gap: '8px' }}>
              <AlertTriangle size={18} />
              <span>{authError}</span>
            </div>
          )}

          <div className="auth-tabs">
            <button
              onClick={() => setAuthMode('login')}
              className={`auth-tab-btn ${authMode === 'login' ? 'auth-tab-btn-active' : ''}`}
            >
              Iniciar Sesión
            </button>
            <button
              onClick={() => setAuthMode('register')}
              className={`auth-tab-btn ${authMode === 'register' ? 'auth-tab-btn-active' : ''}`}
            >
              Registrarse
            </button>
          </div>

          {authMode === 'login' ? (
            <form onSubmit={handleLoginSubmit} style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
              <div className="form-group">
                <label className="form-label">Correo Electrónico</label>
                <input
                  type="email"
                  required
                  className="input-glass"
                  value={authEmail}
                  onChange={e => setAuthEmail(e.target.value)}
                  placeholder="ej. juan@wellness.com"
                />
              </div>

              <div className="form-group">
                <label className="form-label">Contraseña</label>
                <input
                  type="password"
                  required
                  className="input-glass"
                  value={authPassword}
                  onChange={e => setAuthPassword(e.target.value)}
                  placeholder="••••••••"
                />
              </div>

              <button type="submit" className="btn-primary" disabled={loading} style={{ marginTop: '8px' }}>
                {loading ? 'Ingresando...' : 'Ingresar a la Plataforma'}
                <ChevronRight size={18} />
              </button>
            </form>
          ) : (
            <form onSubmit={handleRegisterSubmit} style={{ display: 'flex', flexDirection: 'column', gap: '14px' }}>
              <div style={{ backgroundColor: 'rgba(6, 182, 212, 0.1)', border: '1px solid rgba(6, 182, 212, 0.3)', padding: '10px 14px', borderRadius: '12px', fontSize: '0.75rem', color: 'var(--accent-cyan)' }}>
                ℹ️ <strong>Registro de Atleta / Cliente:</strong> Las cuentas de Entrenadores y Administradores son creadas exclusivamente por la administración del gimnasio.
              </div>

              <div className="form-group">
                <label className="form-label">Nombre Completo</label>
                <input
                  type="text"
                  required
                  className="input-glass"
                  value={authName}
                  onChange={e => setAuthName(e.target.value)}
                  placeholder="Tu nombre completo"
                />
              </div>

              <div className="form-group">
                <label className="form-label">Sucursal del Gimnasio</label>
                <select
                  value={authBranch}
                  onChange={e => setAuthBranch(e.target.value)}
                  className="input-glass select-glass"
                >
                  {branches.length > 0 ? (
                    branches.map((b, i) => (
                      <option key={i} value={b.id}>{b.name} ({b.city})</option>
                    ))
                  ) : (
                    <option value="branch_central">Wellness Fitness Center — Central</option>
                  )}
                </select>
              </div>

              <div className="form-group">
                <label className="form-label">Correo Electrónico</label>
                <input
                  type="email"
                  required
                  className="input-glass"
                  value={authEmail}
                  onChange={e => setAuthEmail(e.target.value)}
                  placeholder="correo@ejemplo.com"
                />
              </div>

              <div className="form-group">
                <label className="form-label">Contraseña</label>
                <input
                  type="password"
                  required
                  className="input-glass"
                  value={authPassword}
                  onChange={e => setAuthPassword(e.target.value)}
                  placeholder="Mínimo 6 caracteres"
                />
              </div>

              <div className="form-group">
                <label className="form-label">Condiciones de Salud / Lesiones</label>
                <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
                  {COMMON_HEALTH_CONDITIONS.map(cond => (
                    <label key={cond} style={{ display: 'flex', alignItems: 'center', gap: '8px', fontSize: '0.8rem', color: 'var(--text-secondary)', cursor: 'pointer' }}>
                      <input
                        type="checkbox"
                        checked={authHealth.includes(cond)}
                        onChange={e => {
                          if (e.target.checked) setAuthHealth([...authHealth, cond]);
                          else setAuthHealth(authHealth.filter(h => h !== cond));
                        }}
                      />
                      {cond}
                    </label>
                  ))}
                </div>
              </div>

              <button type="submit" className="btn-primary" disabled={loading} style={{ marginTop: '8px' }}>
                {loading ? 'Registrando...' : 'Crear Cuenta de Atleta'}
              </button>
            </form>
          )}
        </div>
      </div>
    );
  }

  // ═════════════════════════════════════════════════════════════
  // PANTALLA PRINCIPAL CON NAVEGACIÓN Y DASHBOARD POR ROL
  // ═════════════════════════════════════════════════════════════
  return (
    <div className="app-container app-grid-layout">
      {/* Toast Notification */}
      {toast && (
        <div className="toast-notification">
          <Sparkles size={18} />
          <span>{toast}</span>
        </div>
      )}

      {/* HEADER PRINCIPAL */}
      <header className="app-header">
        <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
          <div className="avatar-ring">
            <Dumbbell size={18} />
          </div>
          <div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
              <h1 className="logo-text">Wellness Lift</h1>
              <span style={{
                padding: '2px 8px',
                borderRadius: '20px',
                fontSize: '0.7rem',
                fontWeight: 700,
                border: '1px solid',
                backgroundColor: userRole === 'admin' ? 'rgba(168, 85, 247, 0.1)' : userRole === 'coach' ? 'rgba(245, 158, 11, 0.1)' : 'rgba(16, 185, 129, 0.1)',
                borderColor: userRole === 'admin' ? 'rgba(168, 85, 247, 0.3)' : userRole === 'coach' ? 'rgba(245, 158, 11, 0.3)' : 'rgba(16, 185, 129, 0.3)',
                color: userRole === 'admin' ? '#c084fc' : userRole === 'coach' ? '#fbbf24' : '#34d399'
              }}>
                {userRole === 'admin' ? 'ADMIN GIMNASIO' : userRole === 'coach' ? 'COACH / ENTRENADOR' : 'ATLETA'}
              </span>
            </div>
            <p style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>Sucursal Central — Gym Cloud System</p>
          </div>
        </div>

        <div style={{ display: 'flex', alignItems: 'center', gap: '16px' }}>
          <div style={{ textAlign: 'right' }}>
            <p style={{ fontSize: '0.85rem', fontWeight: 600, color: 'var(--text-primary)' }}>{userName}</p>
            <p style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>{userEmail}</p>
          </div>

          <button
            onClick={handleLogout}
            className="btn-secondary"
            style={{ width: 'auto', padding: '8px 14px', fontSize: '0.8rem', display: 'flex', alignItems: 'center', gap: '6px' }}
            title="Cerrar Sesión"
          >
            <LogOut size={16} />
            <span>Salir</span>
          </button>
        </div>
      </header>

      {/* TABS DE NAVEGACIÓN SEGÚN ROL */}
      <nav className="tab-navbar">
        {userRole === 'athlete' && (
          <>
            <button
              onClick={() => setCurrentTab('entrenar')}
              className={`tab-btn ${currentTab === 'entrenar' ? 'tab-btn-active' : ''}`}
            >
              <Dumbbell size={20} />
              <span>Mi Rutina</span>
            </button>
            <button
              onClick={() => setCurrentTab('progreso')}
              className={`tab-btn ${currentTab === 'progreso' ? 'tab-btn-active' : ''}`}
            >
              <TrendingUp size={20} />
              <span>Mi Progreso</span>
            </button>
            <button
              onClick={() => setCurrentTab('perfil')}
              className={`tab-btn ${currentTab === 'perfil' ? 'tab-btn-active' : ''}`}
            >
              <Stethoscope size={20} />
              <span>Salud & Solicitudes</span>
            </button>
            <button
              onClick={() => setCurrentTab('chat')}
              className={`tab-btn ${currentTab === 'chat' ? 'tab-btn-active' : ''}`}
            >
              <MessageSquare size={20} />
              <span>Coach IA</span>
            </button>
          </>
        )}

        {userRole === 'coach' && (
          <>
            <button
              onClick={() => setCurrentTab('atletas')}
              className={`tab-btn ${currentTab === 'atletas' ? 'tab-btn-active' : ''}`}
            >
              <Users size={20} />
              <span>Mis Atletas</span>
            </button>
            <button
              onClick={() => setCurrentTab('solicitudes')}
              className={`tab-btn ${currentTab === 'solicitudes' ? 'tab-btn-active' : ''}`}
            >
              <FileText size={20} />
              <span>Solicitudes</span>
              {coachPendingRequests.length > 0 && (
                <span style={{ backgroundColor: '#f59e0b', color: '#020617', padding: '2px 6px', borderRadius: '10px', fontSize: '0.65rem', fontWeight: 800 }}>
                  {coachPendingRequests.length}
                </span>
              )}
            </button>
            <button
              onClick={() => setCurrentTab('chat')}
              className={`tab-btn ${currentTab === 'chat' ? 'tab-btn-active' : ''}`}
            >
              <MessageSquare size={20} />
              <span>Asistente IA</span>
            </button>
          </>
        )}

        {userRole === 'admin' && (
          <>
            <button
              onClick={() => setCurrentTab('usuarios')}
              className={`tab-btn ${currentTab === 'usuarios' ? 'tab-btn-active' : ''}`}
            >
              <Users size={20} />
              <span>Usuarios Globales</span>
            </button>
            <button
              onClick={() => setCurrentTab('sucursales')}
              className={`tab-btn ${currentTab === 'sucursales' ? 'tab-btn-active' : ''}`}
            >
              <Building size={20} />
              <span>Sucursales</span>
            </button>
            <button
              onClick={() => setCurrentTab('coaches')}
              className={`tab-btn ${currentTab === 'coaches' ? 'tab-btn-active' : ''}`}
            >
              <Users size={20} />
              <span>Personal & Staff</span>
            </button>
          </>
        )}
      </nav>

      {/* CONTENIDO PRINCIPAL DE LA VISTA */}
      <main className="app-content">

        {/* ────────────────────────────────────────────────────────── */}
        {/* MODO GIMNASIO: SESIÓN ACTIVA Y EN VIVO DEL ATLETA */}
        {/* ────────────────────────────────────────────────────────── */}
        {activeSession ? (
          <div className="card-glass" style={{ border: '2px solid var(--accent-neon)' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '16px', borderBottom: '1px solid var(--glass-border)', paddingBottom: '12px' }}>
              <div>
                <span style={{ backgroundColor: 'rgba(16, 185, 129, 0.15)', color: '#34d399', padding: '4px 10px', borderRadius: '12px', fontSize: '0.75rem', fontWeight: 800, border: '1px solid rgba(16, 185, 129, 0.3)' }}>
                  🔥 MODO GIMNASIO EN VIVO
                </span>
                <h2 style={{ fontSize: '1.2rem', fontWeight: 800, color: 'var(--text-primary)', marginTop: '6px' }}>{activeSession.day_name}</h2>
              </div>

              <div style={{ textAlign: 'right' }}>
                <p style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>Volumen Acumulado:</p>
                <p style={{ fontSize: '1.2rem', fontWeight: 800, color: 'var(--accent-neon)' }}>
                  {activeSession.exercises.reduce((acc, ex) => acc + ex.sets.filter(s => s.completed).reduce((sAcc, s) => sAcc + (s.weight * s.reps), 0), 0)} kg
                </p>
              </div>
            </div>

            {/* Lista Interactiva de Ejercicios y Series */}
            <div style={{ display: 'flex', flexDirection: 'column', gap: '20px', marginBottom: '24px' }}>
              {activeSession.exercises.map((ex, exIdx) => (
                <div key={exIdx} style={{ background: 'var(--bg-tertiary)', padding: '16px', borderRadius: '14px', border: '1px solid var(--glass-border)' }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '12px' }}>
                    <h3 style={{ fontSize: '0.95rem', fontWeight: 700, color: 'var(--accent-cyan)' }}>{ex.exercise_name}</h3>
                    <button
                      onClick={() => handleAddSetToExercise(exIdx)}
                      className="btn-secondary"
                      style={{ width: 'auto', padding: '4px 10px', fontSize: '0.75rem' }}
                    >
                      + Serie
                    </button>
                  </div>

                  {/* Tabla de Series */}
                  <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
                    {ex.sets.map((s, setIdx) => (
                      <div key={setIdx} style={{
                        display: 'grid', gridTemplateColumns: '40px 1fr 1fr 100px', alignItems: 'center', gap: '10px',
                        background: s.completed ? 'rgba(16, 185, 129, 0.08)' : 'rgba(255, 255, 255, 0.02)',
                        padding: '8px 12px', borderRadius: '10px', border: '1px solid var(--glass-border)'
                      }}>
                        <span style={{ fontWeight: 800, fontSize: '0.85rem', color: 'var(--text-muted)' }}>#{s.set_number}</span>

                        <div style={{ display: 'flex', alignItems: 'center', gap: '4px' }}>
                          <input
                            type="number"
                            className="input-glass"
                            style={{ padding: '6px', textAlign: 'center', fontSize: '0.85rem' }}
                            value={s.weight}
                            onChange={e => handleUpdateSetWeight(exIdx, setIdx, e.target.value)}
                          />
                          <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>kg</span>
                        </div>

                        <div style={{ display: 'flex', alignItems: 'center', gap: '4px' }}>
                          <input
                            type="number"
                            className="input-glass"
                            style={{ padding: '6px', textAlign: 'center', fontSize: '0.85rem' }}
                            value={s.reps}
                            onChange={e => handleUpdateSetReps(exIdx, setIdx, e.target.value)}
                          />
                          <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>reps</span>
                        </div>

                        <button
                          onClick={() => handleToggleSetComplete(exIdx, setIdx)}
                          className="btn-primary"
                          style={{
                            padding: '6px', fontSize: '0.75rem',
                            background: s.completed ? '#10b981' : 'var(--bg-tertiary)',
                            color: s.completed ? '#020617' : 'var(--text-secondary)',
                            border: '1px solid var(--glass-border)'
                          }}
                        >
                          {s.completed ? '✓ Hecho' : 'Completar'}
                        </button>
                      </div>
                    ))}
                  </div>
                </div>
              ))}
            </div>

            <div style={{ display: 'flex', gap: '12px' }}>
              <button onClick={handleFinishWorkout} className="btn-primary" style={{ flex: 1, padding: '14px' }}>
                🏆 Finalizar y Guardar Entrenamiento
              </button>
              <button onClick={() => setActiveSession(null)} className="btn-secondary" style={{ flex: 1, padding: '14px' }}>
                Cancelar Sesión
              </button>
            </div>
          </div>
        ) : null}

        {/* ────────────────────────────────────────────────────────── */}
        {/* VISTAS DE ATLETA: MI PROGRESO Y REGISTRO DÍA A DÍA */}
        {/* ────────────────────────────────────────────────────────── */}
        {userRole === 'athlete' && currentTab === 'progreso' && (
          <div style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
            <div className="card-glass">
              <h2 style={{ fontSize: '1.25rem', fontWeight: 800, color: 'var(--text-primary)' }}>Mi Ficha de Progreso & Historial Deportivo</h2>
              <p style={{ fontSize: '0.85rem', color: 'var(--text-secondary)', marginTop: '4px' }}>Inspecciona lo que entrenaste día por día y sigue la evolución de tus cargas de fuerza.</p>

              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(180px, 1fr))', gap: '12px', marginTop: '16px' }}>
                <div style={{ background: 'var(--bg-tertiary)', padding: '14px', borderRadius: '12px', border: '1px solid var(--glass-border)' }}>
                  <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>Sesiones Completadas:</span>
                  <p style={{ fontSize: '1.4rem', fontWeight: 800, color: 'var(--accent-cyan)', marginTop: '2px' }}>{sessions.length}</p>
                </div>
                <div style={{ background: 'var(--bg-tertiary)', padding: '14px', borderRadius: '12px', border: '1px solid var(--glass-border)' }}>
                  <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>Volumen Total Levantado:</span>
                  <p style={{ fontSize: '1.4rem', fontWeight: 800, color: 'var(--accent-neon)', marginTop: '2px' }}>
                    {sessions.reduce((acc, s) => acc + (s.total_volume || 0), 0)} kg
                  </p>
                </div>
              </div>
            </div>

            {/* Historial de Sesiones Día por Día */}
            <div className="card-glass">
              <h3 style={{ fontSize: '1rem', fontWeight: 700, color: 'var(--text-primary)', marginBottom: '16px' }}>Registro de Sesiones de la Semana (Día a Día)</h3>
              
              <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
                {sessions.length > 0 ? (
                  sessions.map((sess, i) => (
                    <div key={i} style={{ background: 'var(--bg-tertiary)', padding: '16px', borderRadius: '12px', border: '1px solid var(--glass-border)' }}>
                      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '10px' }}>
                        <div>
                          <span style={{ fontSize: '0.9rem', fontWeight: 700, color: 'var(--accent-cyan)' }}>{sess.day_name || 'Sesión Registrada'}</span>
                          <p style={{ fontSize: '0.75rem', color: 'var(--text-muted)', marginTop: '2px' }}>Fecha: {sess.date?.substring(0, 10)}</p>
                        </div>
                        <span style={{ padding: '4px 10px', borderRadius: '12px', fontSize: '0.8rem', fontWeight: 800, backgroundColor: 'rgba(16, 185, 129, 0.15)', color: '#34d399' }}>
                          Volumen: {sess.total_volume} kg
                        </span>
                      </div>

                      <div style={{ display: 'flex', flexDirection: 'column', gap: '6px' }}>
                        {sess.exercises?.map((ex, eI) => (
                          <div key={eI} style={{ fontSize: '0.85rem', color: 'var(--text-secondary)', background: 'rgba(255,255,255,0.02)', padding: '8px 12px', borderRadius: '8px' }}>
                            • <strong>{ex.exercise_name}</strong>: {ex.sets?.map(s => `${s.weight}kg × ${s.reps} reps`).join(' | ')}
                          </div>
                        ))}
                      </div>
                    </div>
                  ))
                ) : (
                  <p style={{ color: 'var(--text-muted)', fontStyle: 'italic', fontSize: '0.85rem' }}>Aún no has registrado entrenamientos completados.</p>
                )}
              </div>
            </div>
          </div>
        )}

        {/* ────────────────────────────────────────────────────────── */}
        {/* VISTAS DE ADMINISTRADOR DE GIMNASIO: DIRECTORIO GLOBAL Y REASIGNACIÓN DE COACHES */}
        {/* ────────────────────────────────────────────────────────── */}
        {userRole === 'admin' && currentTab === 'usuarios' && (
          <div style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
            <div className="card-glass">
              <h2 style={{ fontSize: '1.25rem', fontWeight: 800, color: 'var(--text-primary)' }}>Directorio Global de Usuarios & Control de Cuentas</h2>
              <p style={{ fontSize: '0.85rem', color: 'var(--text-secondary)', marginTop: '4px' }}>Monitorea, edita, traslada sucursal o reasigna entrenadores (coaches) a cada atleta.</p>

              {/* Filtros de Búsqueda */}
              <div style={{ display: 'flex', gap: '12px', marginTop: '16px', flexWrap: 'wrap' }}>
                <div style={{ position: 'relative', flex: 1, minWidth: '220px' }}>
                  <Search size={16} style={{ position: 'absolute', left: '12px', top: '14px', color: 'var(--text-muted)' }} />
                  <input
                    type="text"
                    className="input-glass"
                    style={{ paddingLeft: '38px', fontSize: '0.85rem' }}
                    placeholder="Buscar por nombre o correo..."
                    value={userSearchQuery}
                    onChange={e => setUserSearchQuery(e.target.value)}
                  />
                </div>

                <select
                  value={roleFilter}
                  onChange={e => setRoleFilter(e.target.value)}
                  className="input-glass select-glass"
                  style={{ width: 'auto', minWidth: '160px', fontSize: '0.85rem' }}
                >
                  <option value="todos">Todos los Roles</option>
                  <option value="athlete">Solo Atletas</option>
                  <option value="coach">Solo Coaches</option>
                  <option value="admin">Solo Admins</option>
                </select>
              </div>
            </div>

            {/* Lista de Usuarios */}
            <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
              {filteredAdminUsers.map((u, i) => (
                <div key={i} className="card-glass" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '16px' }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
                    <div className="avatar-ring" style={{ backgroundColor: u.role === 'coach' ? '#f59e0b' : u.role === 'admin' ? '#a855f7' : '#10b981' }}>
                      {u.name?.substring(0, 2).toUpperCase()}
                    </div>
                    <div>
                      <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                        <h3 style={{ fontSize: '0.95rem', fontWeight: 700, color: 'var(--text-primary)' }}>{u.name}</h3>
                        <span style={{
                          padding: '2px 8px', borderRadius: '10px', fontSize: '0.65rem', fontWeight: 800,
                          backgroundColor: u.role === 'admin' ? 'rgba(168,85,247,0.15)' : u.role === 'coach' ? 'rgba(245,158,11,0.15)' : 'rgba(16,185,129,0.15)',
                          color: u.role === 'admin' ? '#c084fc' : u.role === 'coach' ? '#fbbf24' : '#34d399'
                        }}>
                          {u.role.toUpperCase()}
                        </span>
                        <span style={{
                          padding: '2px 8px', borderRadius: '10px', fontSize: '0.65rem', fontWeight: 800,
                          backgroundColor: u.is_active ? 'rgba(16,185,129,0.15)' : 'rgba(239,68,68,0.15)',
                          color: u.is_active ? '#34d399' : '#f87171'
                        }}>
                          {u.is_active ? 'ACTIVO' : 'INACTIVO'}
                        </span>
                      </div>
                      <p style={{ fontSize: '0.75rem', color: 'var(--text-secondary)', marginTop: '2px' }}>
                        {u.email} | Sucursal: <strong style={{ color: 'var(--accent-cyan)' }}>{u.gym_branch_name}</strong>
                      </p>
                      {u.role === 'athlete' && (
                        <p style={{ fontSize: '0.75rem', color: '#fbbf24', marginTop: '2px' }}>
                          Coach Asignado: <strong>{u.assigned_coach_name || 'Sin Asignar'}</strong>
                        </p>
                      )}
                    </div>
                  </div>

                  <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                    {u.role === 'athlete' && (
                      <button
                        onClick={() => { setReassigningAthlete(u); setTargetNewCoachId(u.assigned_coach_id || 'coach_carlos'); }}
                        className="btn-primary"
                        style={{ width: 'auto', padding: '8px 12px', fontSize: '0.75rem', display: 'flex', alignItems: 'center', gap: '4px', background: 'linear-gradient(135deg, #f59e0b, #d97706)' }}
                      >
                        <UserCheck size={14} />
                        <span>Reasignar Coach</span>
                      </button>
                    )}

                    <button
                      onClick={() => openAdminUserEditModal(u)}
                      className="btn-secondary"
                      style={{ width: 'auto', padding: '8px 12px', fontSize: '0.75rem', display: 'flex', alignItems: 'center', gap: '4px' }}
                    >
                      <Edit3 size={14} />
                      <span>Editar</span>
                    </button>

                    {u.role === 'athlete' && (
                      <button
                        onClick={() => handleOpenTechnicalFile(u.user_id)}
                        className="btn-secondary"
                        style={{ width: 'auto', padding: '8px 12px', fontSize: '0.75rem', display: 'flex', alignItems: 'center', gap: '4px' }}
                      >
                        <Eye size={14} />
                        <span>Ficha</span>
                      </button>
                    )}

                    <button
                      onClick={() => handleToggleUserStatus(u.user_id, u.is_active)}
                      className="btn-secondary"
                      style={{
                        width: 'auto', padding: '8px 12px', fontSize: '0.75rem', display: 'flex', alignItems: 'center', gap: '4px',
                        backgroundColor: u.is_active ? 'rgba(239,68,68,0.1)' : 'rgba(16,185,129,0.1)',
                        color: u.is_active ? '#f87171' : '#34d399',
                        borderColor: u.is_active ? 'rgba(239,68,68,0.3)' : 'rgba(16,185,129,0.3)'
                      }}
                    >
                      <Power size={14} />
                      <span>{u.is_active ? 'Inactivar' : 'Activar'}</span>
                    </button>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* ────────────────────────────────────────────────────────── */}
        {/* VISTAS DE ATLETA: MI RUTINA */}
        {/* ────────────────────────────────────────────────────────── */}
        {userRole === 'athlete' && currentTab === 'entrenar' && !activeSession && (
          <div>
            <div className="card-glass" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '16px' }}>
              <div>
                <h2 style={{ fontSize: '1.25rem', fontWeight: 800, color: 'var(--text-primary)' }}>{routine?.focus || 'Rutina Personalizada'}</h2>
                <p style={{ fontSize: '0.85rem', color: 'var(--text-secondary)', marginTop: '4px' }}>Generada con Inteligencia Artificial y adaptada por tu Coach.</p>
              </div>

              <button
                onClick={() => setShowRequestModal(true)}
                className="btn-primary"
                style={{ width: 'auto', padding: '10px 16px', fontSize: '0.85rem' }}
              >
                <FileText size={16} />
                <span>Solicitar Cambio de Rutina</span>
              </button>
            </div>

            {/* Días de Entrenamiento */}
            <div className="routine-grid">
              {routine?.weekly_schedule?.map((day, idx) => (
                <div key={idx} className="card-glass">
                  <h3 style={{ fontSize: '1rem', fontWeight: 700, color: 'var(--accent-cyan)', marginBottom: '12px' }}>{day.day}</h3>
                  <div style={{ display: 'flex', flexDirection: 'column', gap: '8px', marginBottom: '16px' }}>
                    {day.exercises?.map((ex, eIdx) => (
                      <div key={eIdx} style={{ background: 'var(--bg-tertiary)', padding: '10px 14px', borderRadius: '10px', border: '1px solid var(--glass-border)', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                        <div>
                          <p style={{ fontSize: '0.85rem', fontWeight: 600, color: 'var(--text-primary)' }}>{ex.name}</p>
                          <p style={{ fontSize: '0.75rem', color: 'var(--text-secondary)' }}>{ex.sets} series × {ex.reps} reps</p>
                        </div>
                      </div>
                    ))}
                  </div>

                  <button
                    onClick={() => startWorkoutSession(day)}
                    className="btn-primary"
                    style={{ background: 'linear-gradient(135deg, #10b981, #059669)', width: '100%', padding: '10px' }}
                  >
                    <Play size={16} />
                    <span>Iniciar Entrenamiento</span>
                  </button>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* ────────────────────────────────────────────────────────── */}
        {/* VISTA ATLETA: SALUD Y SOLICITUDES */}
        {/* ────────────────────────────────────────────────────────── */}
        {userRole === 'athlete' && currentTab === 'perfil' && (
          <div style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
            <div className="card-glass">
              <h2 style={{ fontSize: '1.1rem', fontWeight: 700, color: 'var(--text-primary)', marginBottom: '8px', display: 'flex', alignItems: 'center', gap: '8px' }}>
                <Stethoscope size={20} color="#06b6d4" />
                <span>Condiciones de Salud y Lesiones Registradas</span>
              </h2>
              <p style={{ fontSize: '0.8rem', color: 'var(--text-secondary)', marginBottom: '16px' }}>El motor de IA y tu Coach utilizan esta información para omitir o reemplazar ejercicios de riesgo biomecánico.</p>

              <div style={{ display: 'flex', flexWrap: 'wrap', gap: '8px' }}>
                {healthConditions.length > 0 ? (
                  healthConditions.map((h, i) => (
                    <span key={i} style={{ backgroundColor: 'rgba(245, 158, 11, 0.1)', border: '1px solid rgba(245, 158, 11, 0.3)', color: '#fbbf24', padding: '6px 12px', borderRadius: '10px', fontSize: '0.8rem', fontWeight: 700, display: 'flex', alignItems: 'center', gap: '6px' }}>
                      <AlertTriangle size={14} />
                      {h}
                    </span>
                  ))
                ) : (
                  <span style={{ color: 'var(--text-muted)', fontSize: '0.85rem', fontStyle: 'italic' }}>Sin condiciones médicas registradas.</span>
                )}
              </div>
            </div>

            {/* Solicitudes Enviadas al Coach */}
            <div className="card-glass">
              <div style={{ display: 'flex', justify: 'space-between', alignItems: 'center', marginBottom: '16px' }}>
                <h3 style={{ fontSize: '1rem', fontWeight: 700, color: 'var(--text-primary)' }}>Historial de Solicitudes a Tu Coach</h3>
                <button
                  onClick={() => setShowRequestModal(true)}
                  className="btn-primary"
                  style={{ width: 'auto', padding: '8px 12px', fontSize: '0.8rem' }}
                >
                  + Nueva Solicitud
                </button>
              </div>

              <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
                {athleteRequests.map((req, i) => (
                  <div key={i} style={{ background: 'var(--bg-tertiary)', padding: '14px', borderRadius: '12px', border: '1px solid var(--glass-border)', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                    <div>
                      <p style={{ fontSize: '0.85rem', fontWeight: 700, color: 'var(--text-primary)' }}>Objetivo: {req.requested_goal} | Días: {req.requested_days?.join(', ')}</p>
                      <p style={{ fontSize: '0.8rem', color: 'var(--text-secondary)', marginTop: '4px' }}>Notas: "{req.notes || 'Sin notas'}"</p>
                      {req.feedback && <p style={{ fontSize: '0.8rem', color: 'var(--accent-cyan)', marginTop: '4px' }}>Feedback del Coach: {req.feedback}</p>}
                    </div>
                    <span style={{
                      padding: '4px 10px',
                      borderRadius: '20px',
                      fontSize: '0.75rem',
                      fontWeight: 800,
                      backgroundColor: req.status === 'approved' ? 'rgba(16, 185, 129, 0.15)' : req.status === 'rejected' ? 'rgba(239, 68, 68, 0.15)' : 'rgba(245, 158, 11, 0.15)',
                      color: req.status === 'approved' ? '#34d399' : req.status === 'rejected' ? '#f87171' : '#fbbf24'
                    }}>
                      {req.status === 'approved' ? 'Aprobada' : req.status === 'rejected' ? 'Rechazada' : 'Pendiente'}
                    </span>
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}

        {/* ────────────────────────────────────────────────────────── */}
        {/* VISTA ENTRENADOR: MIS ATLETAS (CON ACCESO A FICHA TÉCNICA GARANTIZADO) */}
        {/* ────────────────────────────────────────────────────────── */}
        {userRole === 'coach' && currentTab === 'atletas' && (
          <div>
            <div className="card-glass" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <div>
                <h2 style={{ fontSize: '1.25rem', fontWeight: 800, color: 'var(--text-primary)' }}>Mis Atletas Asignados</h2>
                <p style={{ fontSize: '0.85rem', color: 'var(--text-secondary)', marginTop: '4px' }}>Monitorea y personaliza las rutinas, ejercicios y fichas técnicas de tus alumnos.</p>
              </div>
              <span style={{ padding: '6px 14px', borderRadius: '20px', fontSize: '0.8rem', fontWeight: 700, backgroundColor: 'rgba(245, 158, 11, 0.1)', color: '#fbbf24', border: '1px solid rgba(245, 158, 11, 0.3)' }}>
                {coachAthletes.length} Atletas Activos
              </span>
            </div>

            <div className="routine-grid">
              {coachAthletes.map((ath, idx) => (
                <div key={idx} className="card-glass">
                  <div style={{ display: 'flex', alignItems: 'center', gap: '12px', marginBottom: '14px' }}>
                    <div className="avatar-ring" style={{ width: '42px', height: '42px', fontSize: '1rem' }}>
                      {ath.personal_info?.name?.substring(0, 2).toUpperCase() || 'AT'}
                    </div>
                    <div>
                      <h3 style={{ fontSize: '1rem', fontWeight: 700, color: 'var(--text-primary)' }}>{ath.personal_info?.name}</h3>
                      <p style={{ fontSize: '0.8rem', color: 'var(--text-secondary)' }}>{ath.personal_info?.age} años | {ath.physical_metrics?.weight} kg</p>
                    </div>
                  </div>

                  <div style={{ display: 'flex', flexDirection: 'column', gap: '8px', marginBottom: '14px' }}>
                    <div style={{ background: 'var(--bg-tertiary)', padding: '10px 14px', borderRadius: '10px', fontSize: '0.8rem', display: 'flex', justifyContent: 'space-between' }}>
                      <span style={{ color: 'var(--text-muted)' }}>Objetivo:</span>
                      <span style={{ fontWeight: 700, color: 'var(--accent-cyan)', textTransform: 'uppercase' }}>{ath.fitness_profile?.goal}</span>
                    </div>
                  </div>

                  {ath.fitness_profile?.health_conditions?.length > 0 && (
                    <div style={{ backgroundColor: 'rgba(245, 158, 11, 0.1)', border: '1px solid rgba(245, 158, 11, 0.3)', padding: '10px', borderRadius: '10px', marginBottom: '14px' }}>
                      <p style={{ fontSize: '0.75rem', fontWeight: 700, color: '#fbbf24', display: 'flex', alignItems: 'center', gap: '4px', marginBottom: '4px' }}>
                        <AlertTriangle size={14} />
                        Condiciones Médicas:
                      </p>
                      <p style={{ fontSize: '0.8rem', color: 'var(--text-primary)', fontWeight: 600 }}>{ath.fitness_profile.health_conditions.join(', ')}</p>
                    </div>
                  )}

                  <div style={{ display: 'flex', gap: '8px' }}>
                    <button
                      onClick={() => handleOpenCoachRoutineEditor(ath)}
                      className="btn-primary"
                      style={{ flex: 1, padding: '8px 10px', fontSize: '0.8rem' }}
                    >
                      <Edit3 size={14} />
                      <span>Editar Rutina</span>
                    </button>

                    <button
                      onClick={() => handleOpenTechnicalFile(ath.user_id)}
                      className="btn-secondary"
                      style={{ flex: 1, padding: '8px 10px', fontSize: '0.8rem' }}
                    >
                      <Eye size={14} />
                      <span>Ficha Técnica</span>
                    </button>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* ────────────────────────────────────────────────────────── */}
        {/* VISTA ENTRENADOR: SOLICITUDES PENDIENTES DE RUTINA */}
        {/* ────────────────────────────────────────────────────────── */}
        {userRole === 'coach' && currentTab === 'solicitudes' && (
          <div>
            <div className="card-glass">
              <h2 style={{ fontSize: '1.25rem', fontWeight: 800, color: 'var(--text-primary)' }}>Bandeja de Solicitudes de Rutina</h2>
              <p style={{ fontSize: '0.85rem', color: 'var(--text-secondary)', marginTop: '4px' }}>Revisa los pedidos de cambio de rutina de tus atletas. Al aprobar, la IA regenera automáticamente la rutina adaptada.</p>
            </div>

            <div style={{ display: 'flex', flexDirection: 'column', gap: '16px', marginTop: '16px' }}>
              {coachPendingRequests.length > 0 ? (
                coachPendingRequests.map((req, idx) => (
                  <div key={idx} className="card-glass" style={{ display: 'flex', flexDirection: 'column', gap: '14px' }}>
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', borderBottom: '1px solid var(--glass-border)', paddingBottom: '10px' }}>
                      <div>
                        <h3 style={{ fontSize: '1rem', fontWeight: 700, color: 'var(--text-primary)' }}>{req.athlete_name}</h3>
                        <p style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>Solicitado el {req.created_at?.substring(0, 10)}</p>
                      </div>
                      <span style={{ padding: '4px 10px', borderRadius: '20px', fontSize: '0.75rem', fontWeight: 800, backgroundColor: 'rgba(245, 158, 11, 0.15)', color: '#fbbf24' }}>
                        Pendiente de Revisión
                      </span>
                    </div>

                    <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '12px', fontSize: '0.85rem' }}>
                      <div style={{ background: 'var(--bg-tertiary)', padding: '10px', borderRadius: '10px' }}>
                        <span style={{ color: 'var(--text-muted)', display: 'block', fontSize: '0.75rem' }}>Nuevos Días:</span>
                        <span style={{ fontWeight: 700, color: 'var(--accent-cyan)' }}>{req.requested_days?.join(', ')}</span>
                      </div>
                      <div style={{ background: 'var(--bg-tertiary)', padding: '10px', borderRadius: '10px' }}>
                        <span style={{ color: 'var(--text-muted)', display: 'block', fontSize: '0.75rem' }}>Nuevo Objetivo:</span>
                        <span style={{ fontWeight: 700, color: 'var(--accent-cyan)', textTransform: 'uppercase' }}>{req.requested_goal}</span>
                      </div>
                    </div>

                    {req.health_conditions?.length > 0 && (
                      <div style={{ backgroundColor: 'rgba(245, 158, 11, 0.1)', border: '1px solid rgba(245, 158, 11, 0.3)', padding: '10px', borderRadius: '10px', fontSize: '0.8rem' }}>
                        <span style={{ fontWeight: 700, color: '#fbbf24', display: 'block', marginBottom: '2px' }}>⚠️ Condiciones de Salud:</span>
                        <span style={{ color: 'var(--text-primary)', fontWeight: 600 }}>{req.health_conditions.join(', ')}</span>
                      </div>
                    )}

                    <div style={{ background: 'var(--bg-tertiary)', padding: '10px', borderRadius: '10px', fontSize: '0.85rem' }}>
                      <span style={{ color: 'var(--text-muted)', display: 'block', fontSize: '0.75rem' }}>Motivo del Atleta:</span>
                      <p style={{ color: 'var(--text-primary)', fontStyle: 'italic' }}>"{req.notes || 'Sin observaciones'}"</p>
                    </div>

                    <input
                      type="text"
                      className="input-glass"
                      placeholder="Observaciones del coach (opcional)..."
                      value={coachFeedbackInput}
                      onChange={e => setCoachFeedbackInput(e.target.value)}
                    />

                    <div style={{ display: 'flex', gap: '12px' }}>
                      <button
                        onClick={() => handleCoachRequestAction(req.id, 'approve')}
                        className="btn-primary"
                        style={{ flex: 1 }}
                      >
                        Aprobar y Generar con IA
                      </button>
                      <button
                        onClick={() => handleCoachRequestAction(req.id, 'reject')}
                        className="btn-secondary"
                        style={{ flex: 1, backgroundColor: 'rgba(239, 68, 68, 0.1)', color: '#f87171', borderColor: 'rgba(239, 68, 68, 0.3)' }}
                      >
                        Rechazar Solicitud
                      </button>
                    </div>
                  </div>
                ))
              ) : (
                <div className="card-glass" style={{ textAlign: 'center', padding: '40px', color: 'var(--text-muted)', fontSize: '0.9rem' }}>
                  No tienes solicitudes de cambio pendientes.
                </div>
              )}
            </div>
          </div>
        )}

        {/* ────────────────────────────────────────────────────────── */}
        {/* VISTAS ADMINISTRADOR DE GIMNASIO: SUCURSALES Y CREACIÓN DE PERSONAL (COACH / ADMIN) */}
        {/* ────────────────────────────────────────────────────────── */}
        {userRole === 'admin' && currentTab === 'sucursales' && (
          <div>
            <div className="card-glass">
              <h2 style={{ fontSize: '1.25rem', fontWeight: 800, color: 'var(--text-primary)' }}>Sucursales del Gimnasio</h2>
              <p style={{ fontSize: '0.85rem', color: 'var(--text-secondary)', marginTop: '4px' }}>Gestión SaaS Multi-Sucursal para franquicias o sedes de entrenamiento.</p>
            </div>

            <div className="routine-grid" style={{ marginBottom: '20px' }}>
              {branches.map((b, i) => (
                <div key={i} className="card-glass" style={{ display: 'flex', alignItems: 'center', gap: '14px' }}>
                  <Building size={28} color="#c084fc" />
                  <div>
                    <h3 style={{ fontSize: '1rem', fontWeight: 700, color: 'var(--text-primary)' }}>{b.name}</h3>
                    <p style={{ fontSize: '0.8rem', color: 'var(--text-secondary)' }}>{b.city} — {b.address}</p>
                  </div>
                </div>
              ))}
            </div>

            {/* Formulario Crear Sucursal */}
            <form onSubmit={handleAdminCreateBranch} className="card-glass" style={{ display: 'flex', flexDirection: 'column', gap: '14px' }}>
              <h3 style={{ fontSize: '1rem', fontWeight: 700, color: 'var(--text-primary)' }}>Registrar Nueva Sucursal</h3>
              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '12px' }}>
                <input
                  type="text"
                  className="input-glass"
                  placeholder="Nombre Sucursal"
                  value={newBranchName}
                  onChange={e => setNewBranchName(e.target.value)}
                />
                <input
                  type="text"
                  className="input-glass"
                  placeholder="Ciudad / Distrito"
                  value={newBranchCity}
                  onChange={e => setNewBranchCity(e.target.value)}
                />
                <input
                  type="text"
                  className="input-glass"
                  placeholder="Dirección Física"
                  value={newBranchAddress}
                  onChange={e => setNewBranchAddress(e.target.value)}
                />
              </div>
              <button type="submit" className="btn-primary" style={{ width: 'auto', background: 'linear-gradient(135deg, #a855f7, #7e22ce)' }}>
                + Crear Sucursal
              </button>
            </form>
          </div>
        )}

        {userRole === 'admin' && currentTab === 'coaches' && (
          <div>
            <div className="card-glass">
              <h2 style={{ fontSize: '1.25rem', fontWeight: 800, color: 'var(--text-primary)' }}>Plantel de Personal (Coaches & Administradores)</h2>
              <p style={{ fontSize: '0.85rem', color: 'var(--text-secondary)', marginTop: '4px' }}>Registra y administra las credenciales del equipo del gimnasio.</p>
            </div>

            <div className="routine-grid" style={{ marginBottom: '20px' }}>
              {coaches.map((c, i) => (
                <div key={i} className="card-glass">
                  <h3 style={{ fontSize: '1rem', fontWeight: 700, color: 'var(--text-primary)' }}>{c.personal_info?.name || 'Coach'}</h3>
                  <p style={{ fontSize: '0.85rem', color: '#c084fc', marginTop: '2px' }}>{c.specialty || 'Entrenador de Fuerza'}</p>
                  <p style={{ fontSize: '0.75rem', color: 'var(--text-muted)', marginTop: '6px' }}>ID: {c.user_id}</p>
                </div>
              ))}
            </div>

            {/* Formulario para Crear Coach O Administrador */}
            <form onSubmit={handleAdminCreateStaff} className="card-glass" style={{ display: 'flex', flexDirection: 'column', gap: '14px' }}>
              <h3 style={{ fontSize: '1rem', fontWeight: 700, color: 'var(--text-primary)' }}>Alta de Personal del Gimnasio</h3>
              
              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '12px' }}>
                <div className="form-group">
                  <label className="form-label">Tipo de Usuario a Crear</label>
                  <select
                    value={newStaffRole}
                    onChange={e => setNewStaffRole(e.target.value)}
                    className="input-glass select-glass"
                  >
                    <option value="coach">Entrenador / Coach</option>
                    <option value="admin">Administrador del Gimnasio</option>
                  </select>
                </div>

                <div className="form-group">
                  <label className="form-label">Nombre Completo</label>
                  <input
                    type="text"
                    required
                    className="input-glass"
                    placeholder="Nombre completo"
                    value={newStaffName}
                    onChange={e => setNewStaffName(e.target.value)}
                  />
                </div>

                <div className="form-group">
                  <label className="form-label">Correo Electrónico</label>
                  <input
                    type="email"
                    required
                    className="input-glass"
                    placeholder="correo@gimnasio.com"
                    value={newStaffEmail}
                    onChange={e => setNewStaffEmail(e.target.value)}
                  />
                </div>

                <div className="form-group">
                  <label className="form-label">Contraseña Inicial</label>
                  <input
                    type="password"
                    required
                    className="input-glass"
                    placeholder="••••••••"
                    value={newStaffPassword}
                    onChange={e => setNewStaffPassword(e.target.value)}
                  />
                </div>

                <div className="form-group">
                  <label className="form-label">Especialidad / Cargo</label>
                  <input
                    type="text"
                    className="input-glass"
                    placeholder="ej. Rehabilitación o Gerencia"
                    value={newStaffSpecialty}
                    onChange={e => setNewStaffSpecialty(e.target.value)}
                  />
                </div>

                <div className="form-group">
                  <label className="form-label">Sucursal</label>
                  <select
                    value={newStaffBranch}
                    onChange={e => setNewStaffBranch(e.target.value)}
                    className="input-glass select-glass"
                  >
                    {branches.map((b, i) => (
                      <option key={i} value={b.id}>{b.name}</option>
                    ))}
                  </select>
                </div>
              </div>

              <button type="submit" className="btn-primary" style={{ width: 'auto', background: 'linear-gradient(135deg, #a855f7, #7e22ce)' }}>
                + Dar de Alta {newStaffRole === 'admin' ? 'Administrador' : 'Entrenador'}
              </button>
            </form>
          </div>
        )}

        {/* ────────────────────────────────────────────────────────── */}
        {/* CHATBOT IA INTERACTIVO */}
        {/* ────────────────────────────────────────────────────────── */}
        {currentTab === 'chat' && (
          <div className="card-glass chat-container">
            <div style={{ borderBottom: '1px solid var(--glass-border)', paddingBottom: '12px', marginBottom: '12px', display: 'flex', alignItems: 'center', gap: '10px' }}>
              <div className="avatar-ring">
                <Sparkles size={18} />
              </div>
              <div>
                <h2 style={{ fontSize: '1rem', fontWeight: 800, color: 'var(--text-primary)' }}>Wellness Coach IA (OpenRouter Cloud)</h2>
                <p style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>Inteligencia Artificial activa y personalizada</p>
              </div>
            </div>

            <div className="chat-history">
              {chatMessages.map((msg, i) => (
                <div key={i} className={`chat-message ${msg.sender === 'user' ? 'chat-message-user' : 'chat-message-agent'}`}>
                  {msg.text}
                </div>
              ))}
              <div ref={chatEndRef} />
            </div>

            <div className="chat-input-bar">
              <input
                type="text"
                className="input-glass"
                value={chatInput}
                onChange={e => setChatInput(e.target.value)}
                onKeyDown={e => e.key === 'Enter' && handleSendChatMessage()}
                placeholder="Pregunta sobre ejercicios, biomecánica o alternativas..."
              />
              <button onClick={handleSendChatMessage} className="btn-primary" style={{ width: 'auto', padding: '12px 18px' }}>
                <Send size={16} />
              </button>
            </div>
          </div>
        )}

      </main>

      {/* MODAL REASIGNAR / TRANSFERIR COACH DE UN ATLETA */}
      {reassigningAthlete && (
        <div className="modal-overlay">
          <div className="card-glass modal-card" style={{ maxWidth: '460px', padding: '28px' }}>
            <h3 style={{ fontSize: '1.15rem', fontWeight: 800, color: 'var(--text-primary)', marginBottom: '8px' }}>
              🔄 Reasignar Coach — {reassigningAthlete.name}
            </h3>
            <p style={{ fontSize: '0.8rem', color: 'var(--text-secondary)', marginBottom: '18px' }}>
              Selecciona el nuevo Entrenador a cargo de este atleta (ej. si el coach previo cambió de sucursal o no labora en el gimnasio).
            </p>

            <form onSubmit={handleReassignAthleteCoach} style={{ display: 'flex', flexDirection: 'column', gap: '14px' }}>
              <div className="form-group">
                <label className="form-label">Nuevo Coach Asignado</label>
                <select
                  value={targetNewCoachId}
                  onChange={e => setTargetNewCoachId(e.target.value)}
                  className="input-glass select-glass"
                >
                  {coaches.map((c, i) => (
                    <option key={i} value={c.user_id}>{c.personal_info?.name || c.user_id} ({c.specialty})</option>
                  ))}
                </select>
              </div>

              <div style={{ display: 'flex', gap: '10px' }}>
                <button type="submit" className="btn-primary" style={{ flex: 1, background: 'linear-gradient(135deg, #f59e0b, #d97706)' }}>
                  Confirmar Reasignación
                </button>
                <button type="button" onClick={() => setReassigningAthlete(null)} className="btn-secondary" style={{ flex: 1 }}>
                  Cancelar
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* MODAL EDITOR DE RUTINA POR EL COACH */}
      {editingRoutineAthlete && (
        <div className="modal-overlay">
          <div className="card-glass modal-card" style={{ maxWidth: '680px', padding: '28px' }}>
            <h3 style={{ fontSize: '1.2rem', fontWeight: 800, color: 'var(--text-primary)', marginBottom: '4px' }}>
              ✏️ Personalizar Rutina — {editingRoutineAthlete.personal_info?.name}
            </h3>
            <p style={{ fontSize: '0.8rem', color: 'var(--text-secondary)', marginBottom: '18px' }}>Modifica libremente los ejercicios, series y repeticiones recomendados por la IA.</p>

            <form onSubmit={handleSaveCoachCustomRoutine} style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
              <div className="form-group">
                <label className="form-label">Enfoque de la Rutina</label>
                <input
                  type="text"
                  className="input-glass"
                  value={customRoutineFocus}
                  onChange={e => setCustomRoutineFocus(e.target.value)}
                />
              </div>

              {customRoutineSchedule.map((day, dIdx) => (
                <div key={dIdx} style={{ background: 'var(--bg-tertiary)', padding: '16px', borderRadius: '14px', border: '1px solid var(--glass-border)' }}>
                  <input
                    type="text"
                    className="input-glass"
                    style={{ fontWeight: 700, color: 'var(--accent-cyan)', marginBottom: '12px' }}
                    value={day.day}
                    onChange={e => {
                      const updated = [...customRoutineSchedule];
                      updated[dIdx].day = e.target.value;
                      setCustomRoutineSchedule(updated);
                    }}
                  />

                  <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
                    {day.exercises.map((ex, eIdx) => (
                      <div key={eIdx} style={{ display: 'grid', gridTemplateColumns: '2fr 80px 100px 40px', gap: '8px', alignItems: 'center' }}>
                        <input
                          type="text"
                          className="input-glass"
                          style={{ fontSize: '0.8rem' }}
                          value={ex.name}
                          onChange={e => {
                            const updated = [...customRoutineSchedule];
                            updated[dIdx].exercises[eIdx].name = e.target.value;
                            setCustomRoutineSchedule(updated);
                          }}
                        />
                        <input
                          type="number"
                          className="input-glass"
                          style={{ fontSize: '0.8rem', textAlign: 'center' }}
                          value={ex.sets}
                          onChange={e => {
                            const updated = [...customRoutineSchedule];
                            updated[dIdx].exercises[eIdx].sets = parseInt(e.target.value) || 3;
                            setCustomRoutineSchedule(updated);
                          }}
                        />
                        <input
                          type="text"
                          className="input-glass"
                          style={{ fontSize: '0.8rem', textAlign: 'center' }}
                          value={ex.reps}
                          onChange={e => {
                            const updated = [...customRoutineSchedule];
                            updated[dIdx].exercises[eIdx].reps = e.target.value;
                            setCustomRoutineSchedule(updated);
                          }}
                        />
                        <button
                          type="button"
                          onClick={() => {
                            const updated = [...customRoutineSchedule];
                            updated[dIdx].exercises = updated[dIdx].exercises.filter((_, i) => i !== eIdx);
                            setCustomRoutineSchedule(updated);
                          }}
                          style={{ background: 'none', border: 'none', color: '#f87171', cursor: 'pointer', display: 'flex', alignItems: 'center', justifyContent: 'center' }}
                        >
                          <Trash2 size={16} />
                        </button>
                      </div>
                    ))}
                  </div>

                  <button
                    type="button"
                    onClick={() => {
                      const updated = [...customRoutineSchedule];
                      updated[dIdx].exercises.push({ name: "Nuevo Ejercicio", sets: 3, reps: "10-12" });
                      setCustomRoutineSchedule(updated);
                    }}
                    className="btn-secondary"
                    style={{ marginTop: '12px', fontSize: '0.8rem', padding: '8px' }}
                  >
                    + Agregar Ejercicio a este Día
                  </button>
                </div>
              ))}

              <div style={{ display: 'flex', gap: '10px', marginTop: '12px' }}>
                <button type="submit" className="btn-primary" style={{ flex: 1 }}>Guardar Rutina Personalizada</button>
                <button type="button" onClick={() => setEditingRoutineAthlete(null)} className="btn-secondary" style={{ flex: 1 }}>Cancelar</button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* MODAL EDICIÓN COMPLETA DE USUARIO Y RECTIFICACIÓN DE CONTRASEÑA POR EL ADMIN */}
      {editingUserForAdmin && (
        <div className="modal-overlay">
          <div className="card-glass modal-card" style={{ maxWidth: '520px', padding: '28px' }}>
            <h3 style={{ fontSize: '1.15rem', fontWeight: 800, color: 'var(--text-primary)', marginBottom: '14px' }}>
              ✏️ Editar Usuario & Credenciales — {editingUserForAdmin.name}
            </h3>

            <form onSubmit={handleSaveAdminUserEdit} style={{ display: 'flex', flexDirection: 'column', gap: '14px' }}>
              <div className="form-group">
                <label className="form-label">Nombre Completo</label>
                <input type="text" className="input-glass" value={editName} onChange={e => setEditName(e.target.value)} />
              </div>

              <div className="form-group">
                <label className="form-label">Correo Electrónico</label>
                <input type="email" className="input-glass" value={editEmail} onChange={e => setEditEmail(e.target.value)} />
              </div>

              <div className="form-group">
                <label className="form-label" style={{ color: 'var(--accent-neon)', display: 'flex', alignItems: 'center', gap: '4px' }}>
                  <Key size={14} />
                  <span>Restablecer Contraseña (Dejar en blanco para conservar)</span>
                </label>
                <input
                  type="password"
                  className="input-glass"
                  placeholder="Nueva contraseña opcional..."
                  value={editNewPassword}
                  onChange={e => setEditNewPassword(e.target.value)}
                />
              </div>

              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '12px' }}>
                <div className="form-group">
                  <label className="form-label">Rol del Usuario</label>
                  <select value={editRole} onChange={e => setEditRole(e.target.value)} className="input-glass select-glass">
                    <option value="athlete">Atleta</option>
                    <option value="coach">Coach</option>
                    <option value="admin">Administrador</option>
                  </select>
                </div>

                <div className="form-group">
                  <label className="form-label">Sucursal</label>
                  <select value={editBranch} onChange={e => setEditBranch(e.target.value)} className="input-glass select-glass">
                    {branches.map((b, i) => (
                      <option key={i} value={b.id}>{b.name}</option>
                    ))}
                  </select>
                </div>
              </div>

              {editRole === 'athlete' && (
                <div className="form-group">
                  <label className="form-label">Coach Asignado</label>
                  <select value={editCoach} onChange={e => setEditCoach(e.target.value)} className="input-glass select-glass">
                    {coaches.map((c, i) => (
                      <option key={i} value={c.user_id}>{c.personal_info?.name || c.user_id}</option>
                    ))}
                  </select>
                </div>
              )}

              <div style={{ display: 'flex', gap: '10px', marginTop: '12px' }}>
                <button type="submit" className="btn-primary" style={{ flex: 1 }}>Guardar Cambios & Credenciales</button>
                <button type="button" onClick={() => setEditingUserForAdmin(null)} className="btn-secondary" style={{ flex: 1 }}>Cancelar</button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* MODAL FICHA TÉCNICA DEL ATLETA */}
      {selectedTechnicalFile && (
        <div className="modal-overlay">
          <div className="card-glass modal-card" style={{ maxWidth: '680px', padding: '28px' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', borderBottom: '1px solid var(--glass-border)', paddingBottom: '12px', marginBottom: '16px' }}>
              <div>
                <h3 style={{ fontSize: '1.2rem', fontWeight: 800, color: 'var(--text-primary)' }}>Ficha Técnica — {selectedTechnicalFile.personal_info?.name}</h3>
                <p style={{ fontSize: '0.8rem', color: 'var(--text-secondary)' }}>Cliente desde: {selectedTechnicalFile.created_at?.substring(0, 10)} | Antigüedad registrada</p>
              </div>
              <button onClick={() => setSelectedTechnicalFile(null)} className="btn-secondary" style={{ width: 'auto', padding: '6px 14px' }}>Cerrar</button>
            </div>

            {/* Ficha Física y Salud */}
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '12px', marginBottom: '16px', fontSize: '0.85rem' }}>
              <div style={{ background: 'var(--bg-tertiary)', padding: '14px', borderRadius: '12px' }}>
                <span style={{ color: 'var(--text-muted)', display: 'block', fontSize: '0.75rem' }}>Métricas Antropométricas:</span>
                <span style={{ fontWeight: 700, color: 'var(--accent-cyan)' }}>{selectedTechnicalFile.physical_metrics?.weight} kg | {selectedTechnicalFile.physical_metrics?.height} cm</span>
              </div>
              <div style={{ background: 'var(--bg-tertiary)', padding: '14px', borderRadius: '12px' }}>
                <span style={{ color: 'var(--text-muted)', display: 'block', fontSize: '0.75rem' }}>Objetivo Deportivo:</span>
                <span style={{ fontWeight: 700, color: 'var(--accent-neon)', textTransform: 'uppercase' }}>{selectedTechnicalFile.fitness_profile?.goal}</span>
              </div>
            </div>

            {selectedTechnicalFile.fitness_profile?.health_conditions?.length > 0 && (
              <div style={{ backgroundColor: 'rgba(245, 158, 11, 0.1)', border: '1px solid rgba(245, 158, 11, 0.3)', padding: '14px', borderRadius: '12px', marginBottom: '16px', fontSize: '0.8rem' }}>
                <span style={{ fontWeight: 700, color: '#fbbf24', display: 'block', marginBottom: '4px' }}>⚠️ Alertas Médicas & Condiciones de Salud:</span>
                <p style={{ color: 'var(--text-primary)', fontWeight: 600 }}>{selectedTechnicalFile.fitness_profile.health_conditions.join(', ')}</p>
              </div>
            )}

            {/* Récords Personales (PRs) */}
            <div style={{ marginBottom: '16px' }}>
              <h4 style={{ fontSize: '0.9rem', fontWeight: 700, color: 'var(--accent-neon)', marginBottom: '8px', display: 'flex', alignItems: 'center', gap: '6px' }}>
                <Award size={16} />
                <span>Récords Personales de Fuerza (PRs)</span>
              </h4>
              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(180px, 1fr))', gap: '8px' }}>
                {Object.keys(selectedTechnicalFile.personal_records || {}).length > 0 ? (
                  Object.entries(selectedTechnicalFile.personal_records).map(([exName, pr], i) => (
                    <div key={i} style={{ background: 'var(--bg-tertiary)', padding: '12px', borderRadius: '12px', border: '1px solid var(--glass-border)' }}>
                      <p style={{ fontSize: '0.75rem', fontWeight: 600, color: 'var(--text-primary)' }}>{exName}</p>
                      <p style={{ fontSize: '0.9rem', fontWeight: 800, color: 'var(--accent-cyan)' }}>{pr.max_weight} kg × {pr.reps} reps</p>
                    </div>
                  ))
                ) : (
                  <p style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>Sin récords de fuerza registrados aún.</p>
                )}
              </div>
            </div>

            {/* Historial de Sesiones Día a Día */}
            <div>
              <h4 style={{ fontSize: '0.9rem', fontWeight: 700, color: 'var(--text-primary)', marginBottom: '8px' }}>Registro de Sesiones de la Semana (Día por Día)</h4>
              <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
                {selectedTechnicalFile.workout_history?.map((sess, i) => (
                  <div key={i} style={{ background: 'var(--bg-tertiary)', padding: '14px', borderRadius: '12px', border: '1px solid var(--glass-border)' }}>
                    <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '8px' }}>
                      <span style={{ fontSize: '0.85rem', fontWeight: 700, color: 'var(--accent-cyan)' }}>{sess.day_name || 'Sesión de Entrenamiento'}</span>
                      <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>{sess.date?.substring(0, 10)} | Vol: {sess.total_volume} kg</span>
                    </div>

                    <div style={{ display: 'flex', flexDirection: 'column', gap: '6px' }}>
                      {sess.exercises?.map((ex, eI) => (
                        <div key={eI} style={{ fontSize: '0.8rem', color: 'var(--text-secondary)' }}>
                          • <strong>{ex.exercise_name}</strong>: {ex.sets?.map(s => `${s.weight}kg × ${s.reps}`).join(', ')}
                        </div>
                      ))}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>
      )}

      {/* MODAL SOLICITUD DE RUTINA */}
      {showRequestModal && (
        <div className="modal-overlay">
          <div className="card-glass modal-card" style={{ maxWidth: '460px', padding: '28px' }}>
            <h3 style={{ fontSize: '1.15rem', fontWeight: 800, color: 'var(--text-primary)', marginBottom: '16px' }}>Solicitar Cambio de Rutina</h3>
            <form onSubmit={handleCreateRoutineRequest} style={{ display: 'flex', flexDirection: 'column', gap: '14px' }}>
              <div className="form-group">
                <label className="form-label">Nuevo Objetivo Deseado</label>
                <select
                  value={reqGoal}
                  onChange={e => setReqGoal(e.target.value)}
                  className="input-glass select-glass"
                >
                  <option value="hipertrofia">Hipertrofia (Masa Muscular)</option>
                  <option value="fuerza">Fuerza Máxima</option>
                  <option value="definicion">Definición (Pérdida de Grasa)</option>
                </select>
              </div>

              <div className="form-group">
                <label className="form-label">Motivos / Observaciones para tu Coach</label>
                <textarea
                  className="input-glass"
                  style={{ height: '95px', resize: 'none' }}
                  value={reqNotes}
                  onChange={e => setReqNotes(e.target.value)}
                  placeholder="Ej. Quiero aumentar el entrenamiento a 4 días cuidando mi lesión..."
                />
              </div>

              <div style={{ display: 'flex', gap: '10px' }}>
                <button type="submit" className="btn-primary" style={{ flex: 1 }}>Enviar a Coach</button>
                <button type="button" onClick={() => setShowRequestModal(false)} className="btn-secondary" style={{ flex: 1 }}>Cancelar</button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}

export default App;
