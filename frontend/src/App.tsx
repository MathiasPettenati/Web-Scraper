import { useEffect, useMemo, useState } from 'react';

type Product = {
  id: string;
  title: string;
  brand: string;
  category: string;
  color: string;
  condition: string;
  store: string;
  country: string;
  currency: string;
  price: number;
  original_price: number;
  discount_percent: number;
  sizes: string[];
  shipping_cost: number;
  shipping_time: string;
  rating: number;
  popularity: number;
  in_stock: boolean;
  verified: boolean;
  availability: string;
  source_url: string;
  last_verified: string;
  image_url: string;
  description: string;
  tags: string[];
  location_hint: string;
  deal_score: number;
};

type FilterPayload = {
  brands: string[];
  countries: string[];
  stores: string[];
  categories: string[];
  colors: string[];
  sizes: string[];
};

const currencyFormatter = new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD' });

function formatMoney(value: number, currency = 'USD') {
  return new Intl.NumberFormat('en-US', { style: 'currency', currency }).format(value);
}

export default function App() {
  const [theme, setTheme] = useState<'dark' | 'light'>('dark');
  const [products, setProducts] = useState<Product[]>([]);
  const [featured, setFeatured] = useState<Product[]>([]);
  const [filters, setFilters] = useState<FilterPayload | null>(null);
  const [query, setQuery] = useState('');
  const [country, setCountry] = useState('United States');
  const [category, setCategory] = useState('');
  const [brand, setBrand] = useState('');
  const [size, setSize] = useState('');
  const [color, setColor] = useState('');
  const [store, setStore] = useState('');
  const [condition, setCondition] = useState('');
  const [availability, setAvailability] = useState('');
  const [sort, setSort] = useState('best_deal');
  const [loading, setLoading] = useState(true);
  const [selectedProduct, setSelectedProduct] = useState<Product | null>(null);

  useEffect(() => {
    const storedTheme = window.localStorage.getItem('deal-theme');
    if (storedTheme === 'light' || storedTheme === 'dark') {
      setTheme(storedTheme);
    }
  }, []);

  useEffect(() => {
    document.documentElement.classList.toggle('dark', theme === 'dark');
    window.localStorage.setItem('deal-theme', theme);
  }, [theme]);

  useEffect(() => {
    const load = async () => {
      setLoading(true);
      const [productsRes, featuredRes, filtersRes] = await Promise.all([
        fetch(`/api/deals?query=${encodeURIComponent(query)}&country=${encodeURIComponent(country)}&category=${encodeURIComponent(category)}&brand=${encodeURIComponent(brand)}&size=${encodeURIComponent(size)}&color=${encodeURIComponent(color)}&store=${encodeURIComponent(store)}&condition=${encodeURIComponent(condition)}&availability=${encodeURIComponent(availability)}&sort=${sort}&page=1&limit=12`),
        fetch('/api/deals/featured'),
        fetch('/api/deals/filters'),
      ]);
      const [productsJson, featuredJson, filtersJson] = await Promise.all([
        productsRes.json(),
        featuredRes.json(),
        filtersRes.json(),
      ]);
      setProducts(productsJson.items ?? []);
      setFeatured(featuredJson ?? []);
      setFilters(filtersJson);
      setLoading(false);
    };
    load();
  }, [query, country, category, brand, size, color, store, condition, availability, sort]);

  const bestDeal = useMemo(() => products[0], [products]);

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 transition-colors duration-300 dark:bg-slate-950 dark:text-slate-100">
      <div className="mx-auto flex max-w-7xl flex-col gap-6 px-4 py-6 sm:px-6 lg:px-8">
        <header className="rounded-3xl border border-white/10 bg-white/10 p-4 shadow-2xl backdrop-blur md:p-6">
          <div className="flex flex-col gap-4 md:flex-row md:items-center md:justify-between">
            <div>
              <p className="text-sm uppercase tracking-[0.35em] text-cyan-300">Women’s clothing deals</p>
              <h1 className="text-3xl font-semibold sm:text-4xl">Find the best discounts across trusted retailers.</h1>
              <p className="mt-2 max-w-2xl text-sm text-slate-300 sm:text-base">
                Search, compare, and save standout offers with transparent shipping, verified listings, and fast local recommendations.
              </p>
            </div>
            <div className="flex items-center gap-3">
              <button
                onClick={() => setTheme(theme === 'dark' ? 'light' : 'dark')}
                className="rounded-full border border-cyan-400/40 bg-cyan-500/10 px-4 py-2 text-sm font-medium text-cyan-200"
              >
                {theme === 'dark' ? '☀️ Light mode' : '🌙 Dark mode'}
              </button>
            </div>
          </div>
        </header>

        <section className="grid gap-6 lg:grid-cols-[1.45fr_0.8fr]">
          <div className="rounded-3xl border border-white/10 bg-slate-900/80 p-4 shadow-xl sm:p-6">
            <div className="flex flex-col gap-4 lg:flex-row lg:items-end lg:justify-between">
              <label className="flex-1">
                <span className="mb-2 block text-sm font-medium text-slate-300">Search</span>
                <input
                  value={query}
                  onChange={(event) => setQuery(event.target.value)}
                  placeholder="Search dresses, jackets, jeans..."
                  className="w-full rounded-2xl border border-white/10 bg-slate-950/80 px-4 py-3 text-sm outline-none ring-0"
                />
              </label>
              <label>
                <span className="mb-2 block text-sm font-medium text-slate-300">Country</span>
                <select
                  value={country}
                  onChange={(event) => setCountry(event.target.value)}
                  className="rounded-2xl border border-white/10 bg-slate-950/80 px-4 py-3 text-sm"
                >
                  <option>United States</option>
                  <option>Canada</option>
                  <option>United Kingdom</option>
                  <option>Australia</option>
                  <option>Germany</option>
                  <option>France</option>
                  <option>Japan</option>
                </select>
              </label>
            </div>
            <div className="mt-4 grid gap-3 md:grid-cols-2 xl:grid-cols-4">
              <label>
                <span className="mb-2 block text-sm text-slate-400">Category</span>
                <select value={category} onChange={(event) => setCategory(event.target.value)} className="w-full rounded-2xl border border-white/10 bg-slate-950/80 px-3 py-2 text-sm">
                  <option value="">Any</option>
                  {filters?.categories.map((entry) => <option key={entry}>{entry}</option>)}
                </select>
              </label>
              <label>
                <span className="mb-2 block text-sm text-slate-400">Brand</span>
                <select value={brand} onChange={(event) => setBrand(event.target.value)} className="w-full rounded-2xl border border-white/10 bg-slate-950/80 px-3 py-2 text-sm">
                  <option value="">Any</option>
                  {filters?.brands.map((entry) => <option key={entry}>{entry}</option>)}
                </select>
              </label>
              <label>
                <span className="mb-2 block text-sm text-slate-400">Size</span>
                <select value={size} onChange={(event) => setSize(event.target.value)} className="w-full rounded-2xl border border-white/10 bg-slate-950/80 px-3 py-2 text-sm">
                  <option value="">Any</option>
                  {filters?.sizes.map((entry) => <option key={entry}>{entry}</option>)}
                </select>
              </label>
              <label>
                <span className="mb-2 block text-sm text-slate-400">Sort</span>
                <select value={sort} onChange={(event) => setSort(event.target.value)} className="w-full rounded-2xl border border-white/10 bg-slate-950/80 px-3 py-2 text-sm">
                  <option value="best_deal">Best overall deal</option>
                  <option value="lowest_price">Lowest price</option>
                  <option value="highest_discount">Highest discount</option>
                  <option value="newest">Newest listing</option>
                  <option value="popularity">Popularity</option>
                  <option value="rating">Highest rating</option>
                  <option value="fastest_delivery">Fastest delivery</option>
                </select>
              </label>
            </div>
          </div>

          <aside className="rounded-3xl border border-cyan-400/20 bg-cyan-500/10 p-4 shadow-xl">
            <p className="text-sm font-semibold uppercase tracking-[0.25em] text-cyan-300">Best deal</p>
            {bestDeal ? (
              <>
                <h2 className="mt-2 text-xl font-semibold">{bestDeal.title}</h2>
                <p className="mt-1 text-sm text-slate-300">{bestDeal.brand} • {bestDeal.store}</p>
                <div className="mt-4 flex items-end justify-between">
                  <div>
                    <p className="text-2xl font-semibold">{formatMoney(bestDeal.price, bestDeal.currency)}</p>
                    <p className="text-sm text-slate-400">was {formatMoney(bestDeal.original_price, bestDeal.currency)}</p>
                  </div>
                  <span className="rounded-full bg-cyan-500/20 px-3 py-1 text-sm font-medium text-cyan-200">{bestDeal.discount_percent}% off</span>
                </div>
                <button
                  onClick={() => setSelectedProduct(bestDeal)}
                  className="mt-4 w-full rounded-2xl bg-cyan-500 px-4 py-2 font-medium text-slate-950"
                >
                  View details
                </button>
              </>
            ) : (
              <p className="mt-3 text-sm text-slate-300">Adjust the filters to reveal more offers.</p>
            )}
          </aside>
        </section>

        <section className="grid gap-4 lg:grid-cols-[0.9fr_1.1fr]">
          <div className="rounded-3xl border border-white/10 bg-slate-900/70 p-4 shadow-lg">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm uppercase tracking-[0.3em] text-cyan-300">Nearby & local</p>
                <h3 className="text-xl font-semibold">Local pickup and nearby stores</h3>
              </div>
              <button
                onClick={() => {
                  if (navigator.geolocation) {
                    navigator.geolocation.getCurrentPosition(() => window.alert('Location permission granted. Nearby recommendations are ready.'));
                  }
                }}
                className="rounded-full border border-cyan-400/40 px-3 py-2 text-sm"
              >
                Use my location
              </button>
            </div>
            <div className="mt-4 space-y-3">
              <div className="rounded-2xl border border-white/10 bg-slate-950/70 p-3">
                <p className="font-medium">Downtown Pickup Hub</p>
                <p className="mt-1 text-sm text-slate-400">3.2 km away • Same-day pickup available</p>
              </div>
              <div className="rounded-2xl border border-white/10 bg-slate-950/70 p-3">
                <p className="font-medium">Local Retail Annex</p>
                <p className="mt-1 text-sm text-slate-400">5.8 km away • Free pickup on orders over $75</p>
              </div>
            </div>
          </div>

          <div className="rounded-3xl border border-white/10 bg-slate-900/70 p-4 shadow-lg">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm uppercase tracking-[0.3em] text-cyan-300">Best deals</p>
                <h3 className="text-xl font-semibold">Ranked by price, shipping, rating, and reliability</h3>
              </div>
            </div>
            <div className="mt-4 grid gap-3 md:grid-cols-2">
              {featured.map((item) => (
                <div key={item.id} className="rounded-2xl border border-white/10 bg-slate-950/70 p-3">
                  <div className="flex items-start justify-between gap-2">
                    <div>
                      <p className="font-medium">{item.title}</p>
                      <p className="text-sm text-slate-400">{item.store} • {item.country}</p>
                    </div>
                    <span className="rounded-full bg-emerald-500/20 px-2 py-1 text-xs font-medium text-emerald-200">{item.discount_percent}%</span>
                  </div>
                  <p className="mt-2 text-sm text-slate-400">{formatMoney(item.price, item.currency)} • {item.shipping_cost === 0 ? 'Free shipping' : `Shipping ${formatMoney(item.shipping_cost, item.currency)}`}</p>
                </div>
              ))}
            </div>
          </div>
        </section>

        <section className="rounded-3xl border border-white/10 bg-slate-900/70 p-4 shadow-xl sm:p-6">
          <div className="mb-4 flex items-center justify-between">
            <div>
              <p className="text-sm uppercase tracking-[0.3em] text-cyan-300">Catalog</p>
              <h3 className="text-xl font-semibold">Curated women’s fashion deals</h3>
            </div>
            <p className="text-sm text-slate-400">Verified • In stock • Price drop friendly</p>
          </div>
          {loading ? (
            <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-3">
              {Array.from({ length: 6 }).map((_, index) => <div key={index} className="h-56 animate-pulse rounded-3xl bg-slate-800" />)}
            </div>
          ) : (
            <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-3">
              {products.map((product) => (
                <article key={product.id} className="overflow-hidden rounded-3xl border border-white/10 bg-slate-950/80 transition-transform duration-200 hover:-translate-y-1">
                  <img src={product.image_url} alt={product.title} className="h-48 w-full object-cover" />
                  <div className="p-4">
                    <div className="flex items-start justify-between gap-2">
                      <div>
                        <p className="text-sm font-semibold text-cyan-300">{product.brand}</p>
                        <h4 className="text-lg font-semibold">{product.title}</h4>
                      </div>
                      <span className="rounded-full bg-emerald-500/20 px-2 py-1 text-xs font-medium text-emerald-200">{product.discount_percent}%</span>
                    </div>
                    <p className="mt-2 text-sm text-slate-400">{product.description}</p>
                    <div className="mt-3 flex items-center justify-between text-sm">
                      <div>
                        <p className="font-semibold">{formatMoney(product.price, product.currency)}</p>
                        <p className="text-slate-500 line-through">{formatMoney(product.original_price, product.currency)}</p>
                      </div>
                      <div className="text-right text-slate-400">
                        <p>{product.store}</p>
                        <p>{product.shipping_cost === 0 ? 'Free shipping' : formatMoney(product.shipping_cost, product.currency)}</p>
                      </div>
                    </div>
                    <div className="mt-3 flex flex-wrap gap-2">
                      {product.sizes.slice(0, 4).map((size) => <span key={size} className="rounded-full border border-white/10 px-2 py-1 text-xs">{size}</span>)}
                    </div>
                    <div className="mt-4 flex gap-2">
                      <button onClick={() => setSelectedProduct(product)} className="flex-1 rounded-2xl border border-cyan-400/30 bg-cyan-500/10 px-3 py-2 text-sm font-medium text-cyan-200">
                        View details
                      </button>
                      <a href={product.source_url} target="_blank" rel="noreferrer" className="flex-1 rounded-2xl bg-white/10 px-3 py-2 text-center text-sm font-medium text-slate-200">
                        Buy now
                      </a>
                    </div>
                  </div>
                </article>
              ))}
            </div>
          )}
        </section>
      </div>

      {selectedProduct && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-slate-950/80 p-4">
          <div className="w-full max-w-3xl rounded-3xl border border-white/10 bg-slate-900 p-5 shadow-2xl">
            <div className="flex items-start justify-between gap-4">
              <div>
                <p className="text-sm uppercase tracking-[0.3em] text-cyan-300">Product details</p>
                <h3 className="text-2xl font-semibold">{selectedProduct.title}</h3>
              </div>
              <button onClick={() => setSelectedProduct(null)} className="rounded-full border border-white/10 px-3 py-2 text-sm">Close</button>
            </div>
            <div className="mt-4 grid gap-6 md:grid-cols-[1fr_0.9fr]">
              <img src={selectedProduct.image_url} alt={selectedProduct.title} className="h-72 w-full rounded-3xl object-cover" />
              <div>
                <p className="text-sm text-cyan-300">{selectedProduct.brand} • {selectedProduct.store}</p>
                <p className="mt-2 text-sm text-slate-400">{selectedProduct.description}</p>
                <div className="mt-4 rounded-2xl border border-white/10 bg-slate-950/70 p-4">
                  <p className="text-3xl font-semibold">{formatMoney(selectedProduct.price, selectedProduct.currency)}</p>
                  <p className="text-sm text-slate-500 line-through">{formatMoney(selectedProduct.original_price, selectedProduct.currency)}</p>
                  <p className="mt-2 text-sm text-slate-400">{selectedProduct.discount_percent}% off • {selectedProduct.shipping_cost === 0 ? 'Free shipping' : formatMoney(selectedProduct.shipping_cost, selectedProduct.currency)}</p>
                </div>
                <div className="mt-4 flex flex-wrap gap-2">
                  {selectedProduct.sizes.map((size) => <span key={size} className="rounded-full border border-white/10 px-2 py-1 text-sm">{size}</span>)}
                </div>
                <div className="mt-4 flex flex-col gap-2">
                  <a href={selectedProduct.source_url} target="_blank" rel="noreferrer" className="rounded-2xl bg-cyan-500 px-4 py-2 text-center font-semibold text-slate-950">
                    Open original retailer
                  </a>
                  <button className="rounded-2xl border border-white/10 px-4 py-2 text-sm">Save product</button>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
