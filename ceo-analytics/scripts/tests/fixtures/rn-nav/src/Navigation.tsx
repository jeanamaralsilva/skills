const Stack = createNativeStackNavigator()
const Tab = createBottomTabNavigator()
export function Root() {
  return (
    <Tab.Navigator>
      <Tab.Screen name="Home" component={HomeScreen} />
      <Tab.Screen
        name="Profile"
        component={ProfileScreen}
      />
    </Tab.Navigator>
  )
}
const Auth = createNativeStackNavigatorWithAuth()
export function Lazy() {
  return <Auth.Screen name="Moderation" getComponent={() => ModerationScreen} />
}
const HomeTab = createNativeStackNavigatorWithAuth<HomeTabParams>()
